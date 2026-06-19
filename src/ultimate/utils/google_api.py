from collections import namedtuple
from datetime import datetime
import dateutil.parser
import httplib2
import logging

from django.conf import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger("a2u.email_groups")

# Number of times the client library retries a throttled/5xx request with
# exponential backoff before giving up. Replaces the old fixed time.sleep()
# calls that were sprinkled between every member operation.
API_NUM_RETRIES = 5

# Maximum number of sub-requests to send in a single batch HTTP request. The
# Directory API allows up to 1000, but Google recommends keeping batches at or
# below 50 to stay clear of per-batch limits.
API_BATCH_SIZE = 50


# Result of a diff-based group membership sync.
#   target          - number of addresses the group should contain
#   added/removed   - addresses successfully added/removed this run
#   failed_add      - addresses that should have been added but errored
#   failed_remove   - addresses that should have been removed but errored
GroupSyncResult = namedtuple(
    "GroupSyncResult",
    ["target", "added", "removed", "failed_add", "failed_remove"],
)


class GoogleAppsApi:
    http = None

    def __init__(self):
        credentials_file = getattr(settings, "GOOGLE_APPS_API_CREDENTIALS_FILE", False)
        scopes = getattr(settings, "GOOGLE_APPS_API_SCOPES", False)
        account = getattr(settings, "GOOGLE_APPS_API_ACCOUNT", False)

        if credentials_file and scopes and account:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_file, scopes=scopes
            )

            credentials._kwargs["sub"] = account

            self.http = httplib2.Http()
            self.http = credentials.authorize(self.http)

    def prepare_group_for_sync(
        self, group_name, group_id=None, group_email_address=None, force=False
    ):
        logger.debug('Preparing group "{}" for sync...'.format(group_name))

        # force deliberately wipes the group (delete + recreate) for a clean
        # slate. Without force we leave the existing members in place: the
        # diff-based sync_group_members reconciles them, so there is no longer
        # any need to remove everyone up front and re-add them.
        if force:
            self.delete_group(
                group_id=group_id, group_email_address=group_email_address
            )

        return self.get_or_create_group(
            group_email_address=group_email_address, group_name=group_name
        )

    # TODO need paging for when you have over 200 groups
    def get_or_create_group(self, group_email_address, group_name=""):
        logger.debug("  Getting or creating group {}...".format(group_email_address))

        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        groups_response = None
        target_group = None

        try:
            logger.debug("    Looking for existing group...")
            groups_response = (
                service.groups()
                .list(
                    customer="my_customer",
                    domain="lists.annarborultimate.org",
                    query="email={}".format(group_email_address),
                )
                .execute(http=self.http)
            )
        except Exception:
            return None

        if groups_response and groups_response.get("groups"):
            for group in groups_response.get("groups"):
                if group.get("email") == group_email_address:
                    logger.debug("    Group found!")
                    target_group = group

        # couldn't find group, create it
        if not target_group:
            logger.debug(
                "    Group not found...creating {}...".format(group_email_address)
            )

            body = {
                "email": group_email_address,
            }
            if group_name:
                body.update(
                    {
                        "name": group_name,
                    }
                )

            try:
                target_group = (
                    service.groups().insert(body=body).execute(http=self.http)
                )
                logger.debug("    Success!")
            except Exception:
                logger.debug("    Failure!")
                return None

        group_id = target_group.get("id", None)

        return group_id

    def delete_group(self, group_id=None, group_email_address=None):
        logger.debug("  Deleting existing group...")

        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            try:
                groups_response = (
                    service.groups()
                    .list(
                        customer="my_customer",
                        domain="lists.annarborultimate.org",
                        query="email={}".format(group_email_address),
                    )
                    .execute(http=self.http)
                )

                if groups_response and groups_response.get("groups"):
                    for group in groups_response.get("groups"):
                        if group.get("email") == group_email_address:
                            group_id = group.get("id", None)
            except Exception:
                return False

        if group_id:
            try:
                service.groups().delete(groupKey=group_id).execute(http=self.http)
                logger.debug("    Success!")
            except Exception:
                logger.debug("    Failure!")
                return False

        return True

    def remove_all_group_members(
        self, group_id=None, group_email_address=None, group_name=None
    ):
        logger.debug("  Removing all members from {}...".format(group_email_address))

        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            try:
                groups_response = (
                    service.groups()
                    .list(
                        customer="my_customer",
                        domain="lists.annarborultimate.org",
                        query="email={}".format(group_email_address),
                    )
                    .execute(http=self.http)
                )

                if groups_response and groups_response.get("groups"):
                    for group in groups_response.get("groups"):
                        if group.get("email") == group_email_address:
                            group_id = group.get("id", None)
            except Exception:
                logger.debug("    Group could not be found")
                return False

        if group_id:
            try:
                members_response = (
                    service.members().list(groupKey=group_id).execute(http=self.http)
                )
                if members_response and members_response.get("members"):
                    logger.debug(
                        "  Removing {} members from {}...".format(
                            members_response.get("members"), group_email_address
                        )
                    )
                    for member in members_response.get("members"):
                        member_id = member.get("id", None)
                        service.members().delete(
                            groupKey=group_id, memberKey=member_id
                        ).execute(http=self.http, num_retries=API_NUM_RETRIES)
            except Exception:
                logger.debug("    Group could not be found")
                return False

        logger.debug("    Done")

    def _resolve_group_id(self, service, group_email_address):
        """Look up a group's id by its email address. Returns None if not found."""
        try:
            groups_response = (
                service.groups()
                .list(
                    customer="my_customer",
                    domain="lists.annarborultimate.org",
                    query="email={}".format(group_email_address),
                )
                .execute(http=self.http)
            )
        except Exception:
            return None

        if groups_response and groups_response.get("groups"):
            for group in groups_response.get("groups"):
                if group.get("email") == group_email_address:
                    return group.get("id", None)

        return None

    def list_group_members(self, group_id=None, group_email_address=None):
        """Return the set of lowercased member email addresses for a group.

        Pages through the full membership (the Directory API returns at most
        200 members per response) so callers get every member, not just the
        first page. Returns an empty set if the group can't be resolved.
        """
        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            group_id = self._resolve_group_id(service, group_email_address)

        emails = set()

        if not group_id:
            return emails

        page_token = None
        while True:
            try:
                members_response = (
                    service.members()
                    .list(groupKey=group_id, pageToken=page_token)
                    .execute(http=self.http, num_retries=API_NUM_RETRIES)
                )
            except Exception:
                logger.debug("    Members could not be listed")
                break

            for member in members_response.get("members", []):
                email = member.get("email")
                if email:
                    emails.add(email.lower())

            page_token = members_response.get("nextPageToken")
            if not page_token:
                break

        return emails

    def _execute_batch(self, service, operations, ok_statuses=()):
        """Run member operations in batched HTTP requests.

        ``operations`` is a list of (email_address, request) tuples, where each
        request is an unexecuted googleapiclient request (e.g. a members insert
        or delete). Requests are sent in chunks of API_BATCH_SIZE.

        An HTTP error whose status is listed in ``ok_statuses`` is treated as
        success (e.g. 409 "already a member" on an add, 404 "not a member" on a
        delete). Returns (succeeded_emails, failed_emails) as two lists, where
        failed_emails holds the addresses whose operation genuinely errored.
        """
        succeeded = []
        failed = []

        for start in range(0, len(operations), API_BATCH_SIZE):
            chunk = operations[start : start + API_BATCH_SIZE]

            # Map the synthetic request id back to the email it belongs to so
            # the callback can record per-address success/failure.
            id_to_email = {}

            def callback(request_id, response, exception, id_to_email=id_to_email):
                email = id_to_email.get(request_id)
                if exception is None:
                    succeeded.append(email)
                elif (
                    isinstance(exception, HttpError)
                    and exception.resp.status in ok_statuses
                ):
                    succeeded.append(email)
                else:
                    logger.debug("  Failure for {}: {}".format(email, exception))
                    failed.append(email)

            batch = service.new_batch_http_request(callback=callback)
            for email_address, request in chunk:
                request_id = str(len(id_to_email) + 1)
                id_to_email[request_id] = email_address
                batch.add(request, request_id=request_id)

            try:
                batch.execute(http=self.http)
            except Exception as error:
                # A whole-batch transport failure: none of this chunk's
                # callbacks fired, so count every address in it as failed.
                logger.debug("  Batch request failed: {}".format(error))
                failed.extend(email for email, _ in chunk)

        return succeeded, failed

    def sync_group_members(
        self, desired_emails, group_id=None, group_email_address=None
    ):
        """Make a group's membership match ``desired_emails`` with minimal calls.

        Lists the current members, diffs against the desired set, and only adds
        the addresses that are missing and removes the ones that should no
        longer be there -- rather than emptying the group and re-adding
        everyone. Adds and removes are sent in batched HTTP requests.

        ``desired_emails`` is any iterable of email addresses (case is
        normalized). Returns a GroupSyncResult.
        """
        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            group_id = self._resolve_group_id(service, group_email_address)

        desired = {email.lower() for email in desired_emails if email}
        target = len(desired)

        if not group_id:
            logger.debug("  Group could not be resolved for sync")
            return GroupSyncResult(
                target=target,
                added=[],
                removed=[],
                failed_add=sorted(desired),
                failed_remove=[],
            )

        current = self.list_group_members(group_id=group_id)

        to_add = sorted(desired - current)
        to_remove = sorted(current - desired)

        logger.debug(
            "  Sync {}: {} desired, {} current, {} to add, {} to remove".format(
                group_email_address or group_id,
                target,
                len(current),
                len(to_add),
                len(to_remove),
            )
        )

        add_ops = [
            (
                email,
                service.members().insert(
                    groupKey=group_id, body={"email": email, "role": "MEMBER"}
                ),
            )
            for email in to_add
        ]
        # 409: address is already a member -> already in the desired state.
        added, failed_add = self._execute_batch(service, add_ops, ok_statuses=(409,))

        remove_ops = [
            (email, service.members().delete(groupKey=group_id, memberKey=email))
            for email in to_remove
        ]
        # 404: address is not a member -> already in the desired state.
        removed, failed_remove = self._execute_batch(
            service, remove_ops, ok_statuses=(404,)
        )

        return GroupSyncResult(
            target=target,
            added=added,
            removed=removed,
            failed_add=failed_add,
            failed_remove=failed_remove,
        )

    def add_group_member(
        self, email_address, group_id=None, group_email_address=None, group_name=None
    ):
        logger.debug(
            "Adding {} to {}...".format(email_address, group_email_address or "group")
        )

        service = build("admin", "directory_v1", http=self.http, cache_discovery=False)

        body = {"email": email_address, "role": "MEMBER"}
        response = False

        # look for group
        if not group_id and group_email_address:
            group_id = self.get_or_create_group(
                group_email_address=group_email_address, group_name=group_name
            )

        if group_id:
            try:
                response = (
                    service.members()
                    .insert(groupKey=group_id, body=body)
                    .execute(http=self.http, num_retries=API_NUM_RETRIES)
                )
                logger.debug("  Success!")
            except HttpError as error:
                # A 409 means the address is already a member, which for a sync
                # is a success, not a failure -- treat it as already present.
                if error.resp.status == 409:
                    logger.debug("  Already a member!")
                    return True
                logger.debug("  Failure! {}".format(error))
                return False

        return response

    def get_calendar_events(self, calendar_id, since, until):
        service = build(
            serviceName="calendar", version="v3", http=self.http, cache_discovery=False
        )

        since = (
            datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - since
        ).isoformat("T") + "Z"
        until = (
            datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + until
        ).isoformat("T") + "Z"

        try:
            events_response = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    orderBy="startTime",
                    singleEvents=True,
                    timeMin=since,
                    timeMax=until,
                )
                .execute(http=self.http)
            )
        except Exception:
            return None

        events = []
        for event in events_response["items"]:
            events.append(
                {
                    "summary": event.get("summary"),
                    "start": dateutil.parser.parse(event["start"]["dateTime"]),
                    "end": event["end"]["dateTime"],
                    "location": event.get("location"),
                    "description": event.get("description"),
                }
            )

        return events
