"""Tests for the import_email_group management command.

Covers up-front argument validation and end-to-end dispatch for the team,
league, and pickup sync modes. The Google API is replaced with a fake that
records the desired-email sets it is asked to sync and returns canned
GroupSyncResults, so these exercise the command + model wiring without
network or credentials.
"""

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

from ultimate.utils import google_api
from ultimate.utils.google_api import GroupSyncResult
from ultimate.leagues.tests import factories as f


class FakeApi(object):
    """Records sync calls; returns a fully-successful result by default."""

    calls = []

    def __init__(self):
        pass

    def prepare_group_for_sync(self, group_name, group_id=None,
                               group_email_address=None, force=False):
        return group_id or "gid-for-{}".format(group_email_address)

    def sync_group_members(self, desired_emails, group_id=None,
                           group_email_address=None):
        desired = {e.lower() for e in desired_emails if e}
        FakeApi.calls.append(
            {"group": group_email_address, "desired": desired}
        )
        return GroupSyncResult(
            target=len(desired),
            added=sorted(desired),
            removed=[],
            failed_add=[],
            failed_remove=[],
        )


def patch_api(testcase):
    orig = google_api.GoogleAppsApi
    google_api.GoogleAppsApi = FakeApi
    FakeApi.calls = []
    testcase.addCleanup(lambda: setattr(google_api, "GoogleAppsApi", orig))


class ArgValidationTest(TestCase):
    def _run(self, *args):
        call_command("import_email_group", *args, stdout=StringIO())

    def test_email_without_group_address_errors(self):
        with self.assertRaises(CommandError):
            self._run("-e", "a@x.com")

    def test_file_without_group_address_errors(self):
        with self.assertRaises(CommandError):
            self._run("-f", "/tmp/emails.txt")

    def test_season_without_year_errors(self):
        with self.assertRaises(CommandError):
            self._run("-s", "spring")

    def test_year_without_season_errors(self):
        with self.assertRaises(CommandError):
            self._run("-y", "2026")

    def test_non_numeric_year_errors(self):
        with self.assertRaises(CommandError):
            self._run("-s", "spring", "-y", "notayear")


class TeamSyncCommandTest(TestCase):
    def setUp(self):
        patch_api(self)
        self.season = f.make_season("spring")
        self.league = f.make_league(self.season, 2026)
        self.team = f.make_team(self.league)
        f.add_player(self.team, "alice@x.com")
        f.add_player(self.team, "bob@x.com")

    def test_team_sync_passes_member_emails(self):
        out = StringIO()
        call_command("import_email_group", "-t", str(self.team.id), stdout=out)

        self.assertEqual(len(FakeApi.calls), 1)
        self.assertEqual(
            FakeApi.calls[0]["desired"], {"alice@x.com", "bob@x.com"}
        )
        self.assertIn("SUCCESS", out.getvalue())

    def test_missing_team_reports_error(self):
        out = StringIO()
        call_command("import_email_group", "-t", "99999", stdout=out)

        self.assertEqual(FakeApi.calls, [])
        self.assertIn("No team found", out.getvalue())


class PickupSyncCommandTest(TestCase):
    def setUp(self):
        patch_api(self)
        self.seasons = {
            slug: f.make_season(slug)
            for slug in ["winter", "spring", "summer", "fall", "late-fall"]
        }

    def _add(self, season_slug, year, email):
        team = f.make_team(f.make_league(self.seasons[season_slug], year))
        f.add_player(team, email)

    def test_pickup_sync_uses_season_window(self):
        self._add("winter", 2026, "winter@x.com")
        self._add("spring", 2026, "spring@x.com")
        self._add("summer", 2026, "summer@x.com")
        self._add("fall", 2026, "fall@x.com")  # out of window for summer

        out = StringIO()
        call_command(
            "import_email_group", "-s", "summer", "-y", "2026", "-p", stdout=out
        )

        self.assertEqual(len(FakeApi.calls), 1)
        call = FakeApi.calls[0]
        self.assertEqual(
            call["desired"], {"winter@x.com", "spring@x.com", "summer@x.com"}
        )
        self.assertIn("summer26-pickups@lists.annarborultimate.org", call["group"])

    def test_season_sync_without_pickup_is_not_implemented(self):
        with self.assertRaises(CommandError):
            call_command(
                "import_email_group", "-s", "summer", "-y", "2026",
                stdout=StringIO(),
            )
