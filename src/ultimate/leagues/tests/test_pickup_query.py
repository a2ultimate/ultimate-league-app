"""DB-backed tests for the table-driven pickup season-window query.

The pickup list for a season is built from PICKUP_SEASON_WINDOWS: the target
season plus the seasons leading into it. These tests stand up real rows for
several seasons/years and assert _pickup_emails pulls exactly the right people
-- the behavior the old hand-written Q-block chain used to produce.
"""

from django.test import TestCase

from ultimate.leagues.management.commands.import_email_group import (
    Command,
    PICKUP_SEASON_WINDOWS,
)
from ultimate.leagues.models import TeamMember
from ultimate.leagues.tests import factories as f


class PickupQueryTest(TestCase):
    def setUp(self):
        self.command = Command()
        # One season row per slug, reused across years via make_league(year=).
        self.seasons = {
            slug: f.make_season(slug)
            for slug in ["winter", "spring", "summer", "fall", "late-fall"]
        }

    def _add_member(self, season_slug, year, email):
        league = f.make_league(self.seasons[season_slug], year)
        team = f.make_team(league)
        return f.add_player(team, email)

    def _pickup(self, season_slug, year):
        return self.command._pickup_emails(TeamMember, season_slug, str(year))

    def test_summer_pulls_winter_spring_summer_same_year(self):
        self._add_member("winter", 2026, "winter@x.com")
        self._add_member("spring", 2026, "spring@x.com")
        self._add_member("summer", 2026, "summer@x.com")
        # Out of window: fall is after summer; spring of a different year.
        self._add_member("fall", 2026, "fall@x.com")
        self._add_member("spring", 2025, "spring-prev@x.com")

        emails = self._pickup("summer", 2026)

        self.assertEqual(
            emails, {"winter@x.com", "spring@x.com", "summer@x.com"}
        )

    def test_winter_pulls_prior_year_fall_and_late_fall(self):
        # winter's window is fall(-1), late-fall(-1), winter(0).
        self._add_member("fall", 2025, "fall25@x.com")
        self._add_member("late-fall", 2025, "latefall25@x.com")
        self._add_member("winter", 2026, "winter26@x.com")
        # Out of window: this year's fall, last year's winter.
        self._add_member("fall", 2026, "fall26@x.com")
        self._add_member("winter", 2025, "winter25@x.com")

        emails = self._pickup("winter", 2026)

        self.assertEqual(
            emails, {"fall25@x.com", "latefall25@x.com", "winter26@x.com"}
        )

    def test_spring_pulls_prior_late_fall_and_this_winter_spring(self):
        self._add_member("late-fall", 2025, "latefall25@x.com")
        self._add_member("winter", 2026, "winter26@x.com")
        self._add_member("spring", 2026, "spring26@x.com")

        emails = self._pickup("spring", 2026)

        self.assertEqual(
            emails,
            {"latefall25@x.com", "winter26@x.com", "spring26@x.com"},
        )

    def test_late_fall_pulls_summer_and_fall_but_not_itself(self):
        self._add_member("summer", 2026, "summer@x.com")
        self._add_member("fall", 2026, "fall@x.com")
        # A late-fall member of the same year must NOT be included.
        self._add_member("late-fall", 2026, "latefall@x.com")

        emails = self._pickup("late-fall", 2026)

        self.assertEqual(emails, {"summer@x.com", "fall@x.com"})
        self.assertNotIn("latefall@x.com", emails)

    def test_deduplicates_player_in_multiple_window_seasons(self):
        # The same user plays in two contributing seasons -> appears once.
        user = f.make_user("repeat@x.com")
        winter_team = f.make_team(f.make_league(self.seasons["winter"], 2026))
        spring_team = f.make_team(f.make_league(self.seasons["spring"], 2026))
        f.make_team_member(winter_team, user)
        f.make_team_member(spring_team, user)

        emails = self._pickup("summer", 2026)

        self.assertEqual(emails, {"repeat@x.com"})

    def test_unknown_season_returns_empty(self):
        self._add_member("summer", 2026, "summer@x.com")
        self.assertEqual(self._pickup("offseason", 2026), set())

    def test_window_table_covers_all_real_seasons(self):
        # Guard against a season slug silently missing from the table.
        self.assertEqual(
            set(PICKUP_SEASON_WINDOWS),
            {"winter", "spring", "summer", "fall", "late-fall"},
        )
