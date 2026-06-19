"""Tests for the diff-based group sync in GoogleAppsApi.

These exercise the new core -- list (with paging), diff, batched add/remove,
and the 409/404 "already in the desired state" handling -- against a fake
Directory service so no network or credentials are needed.
"""

from googleapiclient.errors import HttpError
from django.test import TestCase

from ultimate.utils import google_api
from ultimate.utils.google_api import API_BATCH_SIZE, GoogleAppsApi


class _Resp(object):
    """Minimal stand-in for an httplib2 response on an HttpError."""

    def __init__(self, status):
        self.status = status
        self.reason = "test"


def http_error(status):
    return HttpError(_Resp(status), b"{}", uri="http://test")


class FakeWriteRequest(object):
    """An unexecuted insert/delete request; carries the email it targets."""

    def __init__(self, kind, email):
        self.kind = kind
        self.email = email


class FakeListRequest(object):
    def __init__(self, service):
        self.service = service

    def execute(self, http=None, num_retries=0):
        if self.service.list_error is not None:
            raise self.service.list_error
        # Return configured pages in order; default to a single empty page.
        if self.service.pages:
            return self.service.pages.pop(0)
        return {}


class FakeMembers(object):
    def __init__(self, service):
        self.service = service

    def list(self, groupKey=None, pageToken=None):
        return FakeListRequest(self.service)

    def insert(self, groupKey=None, body=None):
        return FakeWriteRequest("insert", body["email"])

    def delete(self, groupKey=None, memberKey=None):
        return FakeWriteRequest("delete", memberKey)


class FakeBatch(object):
    def __init__(self, service, callback):
        self.service = service
        self.callback = callback
        self.items = []

    def add(self, request, request_id=None):
        self.items.append((request_id, request))

    def execute(self, http=None):
        if self.service.batch_error is not None:
            raise self.service.batch_error
        for request_id, request in self.items:
            outcome = self.service.outcomes.get(request.email)
            if outcome is None:
                self.callback(request_id, {"ok": True}, None)
            else:
                self.callback(request_id, None, outcome)


class FakeService(object):
    """Configurable fake of a built Directory API service.

    pages    -- list of members().list() response dicts, returned in order
    outcomes -- email -> HttpError to raise for that email's batch op
                (absent email == success)
    """

    def __init__(self, pages=None, outcomes=None):
        self.pages = list(pages) if pages else []
        self.outcomes = outcomes or {}
        self.list_error = None
        self.batch_error = None
        self.batches = []
        self._members = FakeMembers(self)

    def members(self):
        return self._members

    def new_batch_http_request(self, callback=None):
        batch = FakeBatch(self, callback)
        self.batches.append(batch)
        return batch


def members_page(emails, next_token=None):
    page = {"members": [{"email": e} for e in emails]}
    if next_token:
        page["nextPageToken"] = next_token
    return page


class SyncGroupMembersTest(TestCase):
    def setUp(self):
        self.api = GoogleAppsApi()  # http=None under test settings

    def _patch_service(self, service):
        # Both list_group_members and sync_group_members build their own
        # service; return the same fake from every build() call.
        self._build_patch = _PatchBuild(service)
        self._build_patch.start()
        self.addCleanup(self._build_patch.stop)

    def test_diff_adds_missing_and_removes_stale(self):
        service = FakeService(pages=[members_page(["a@x.com", "b@x.com"])])
        self._patch_service(service)

        result = self.api.sync_group_members(
            ["b@x.com", "c@x.com"], group_id="gid"
        )

        self.assertEqual(result.target, 2)
        self.assertEqual(result.added, ["c@x.com"])
        self.assertEqual(result.removed, ["a@x.com"])
        self.assertEqual(result.failed_add, [])
        self.assertEqual(result.failed_remove, [])

    def test_no_change_makes_no_writes(self):
        service = FakeService(pages=[members_page(["a@x.com", "b@x.com"])])
        self._patch_service(service)

        result = self.api.sync_group_members(
            ["a@x.com", "b@x.com"], group_id="gid"
        )

        self.assertEqual(result.added, [])
        self.assertEqual(result.removed, [])
        # A no-op sync should not even open a batch request.
        self.assertEqual([b for b in service.batches if b.items], [])

    def test_email_case_is_normalized(self):
        service = FakeService(pages=[members_page(["a@x.com"])])
        self._patch_service(service)

        result = self.api.sync_group_members(["A@X.com"], group_id="gid")

        # "A@X.com" lower-cases to the existing "a@x.com": nothing to do.
        self.assertEqual(result.added, [])
        self.assertEqual(result.removed, [])
        self.assertEqual(result.target, 1)

    def test_409_on_add_counts_as_success(self):
        service = FakeService(
            pages=[members_page([])], outcomes={"dup@x.com": http_error(409)}
        )
        self._patch_service(service)

        result = self.api.sync_group_members(["dup@x.com"], group_id="gid")

        self.assertEqual(result.added, ["dup@x.com"])
        self.assertEqual(result.failed_add, [])

    def test_404_on_remove_counts_as_success(self):
        service = FakeService(
            pages=[members_page(["gone@x.com"])],
            outcomes={"gone@x.com": http_error(404)},
        )
        self._patch_service(service)

        result = self.api.sync_group_members([], group_id="gid")

        self.assertEqual(result.removed, ["gone@x.com"])
        self.assertEqual(result.failed_remove, [])

    def test_genuine_error_is_reported_as_failed(self):
        service = FakeService(
            pages=[members_page([])], outcomes={"bad@x.com": http_error(500)}
        )
        self._patch_service(service)

        result = self.api.sync_group_members(["bad@x.com"], group_id="gid")

        self.assertEqual(result.added, [])
        self.assertEqual(result.failed_add, ["bad@x.com"])

    def test_unresolved_group_reports_all_desired_as_failed_add(self):
        service = FakeService(pages=[members_page([])])
        self._patch_service(service)

        # No group_id and no resolvable address -> nothing can be synced.
        result = self.api.sync_group_members(["a@x.com"], group_id=None)

        self.assertEqual(result.added, [])
        self.assertEqual(sorted(result.failed_add), ["a@x.com"])

    def test_adds_are_chunked_into_batches(self):
        service = FakeService(pages=[members_page([])])
        self._patch_service(service)

        desired = ["u{}@x.com".format(i) for i in range(API_BATCH_SIZE + 10)]
        result = self.api.sync_group_members(desired, group_id="gid")

        self.assertEqual(len(result.added), API_BATCH_SIZE + 10)
        # API_BATCH_SIZE + 10 adds should span two batches of <= API_BATCH_SIZE.
        add_batches = [b for b in service.batches if b.items]
        self.assertEqual(len(add_batches), 2)
        self.assertTrue(all(len(b.items) <= API_BATCH_SIZE for b in add_batches))

    def test_whole_batch_failure_marks_all_failed(self):
        service = FakeService(pages=[members_page([])])
        service.batch_error = RuntimeError("network down")
        self._patch_service(service)

        result = self.api.sync_group_members(
            ["a@x.com", "b@x.com"], group_id="gid"
        )

        self.assertEqual(result.added, [])
        self.assertEqual(sorted(result.failed_add), ["a@x.com", "b@x.com"])


class ListGroupMembersTest(TestCase):
    def setUp(self):
        self.api = GoogleAppsApi()

    def test_pages_through_all_members(self):
        service = FakeService(
            pages=[
                members_page(["a@x.com", "b@x.com"], next_token="t2"),
                members_page(["c@x.com"]),
            ]
        )
        patch = _PatchBuild(service)
        patch.start()
        self.addCleanup(patch.stop)

        emails = self.api.list_group_members(group_id="gid")

        self.assertEqual(emails, {"a@x.com", "b@x.com", "c@x.com"})

    def test_returns_empty_set_without_group(self):
        service = FakeService(pages=[members_page([])])
        patch = _PatchBuild(service)
        patch.start()
        self.addCleanup(patch.stop)

        self.assertEqual(self.api.list_group_members(group_id=None), set())


class _PatchBuild(object):
    """Patch google_api.build to return a fixed fake service."""

    def __init__(self, service):
        self.service = service
        self._orig = None

    def start(self):
        self._orig = google_api.build
        google_api.build = lambda *args, **kwargs: self.service

    def stop(self):
        google_api.build = self._orig
