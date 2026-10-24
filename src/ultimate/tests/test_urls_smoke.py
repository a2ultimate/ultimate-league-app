"""URL-resolution smoke tests.

The single highest-value guard for the Django upgrade: every named URL in the
project must reverse to a path. This catches the routing-layer breakage that the
upgrade churns through -- the move of ``reverse`` from ``django.core.urlresolvers``
to ``django.urls`` (Django 2.0), and the removal of ``django.conf.urls.url`` in
favor of ``re_path``/``path`` (Django 4.0). If a URLconf fails to import or a name
is dropped during conversion, these assertions fail immediately.

The named patterns are enumerated explicitly (rather than walked from the
resolver) so that a name silently disappearing is itself a test failure.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import NoReverseMatch, reverse


# (url_name, kwargs) for every named route the project defines. Routes that take
# captured arguments get representative values; the goal is that the name exists
# and the pattern accepts these args, not that the target view does anything.
LEAGUE_KWARGS = {"year": "2026", "season": "summer", "division": "sunday"}

NAMED_ROUTES = [
    # index
    ("home", {}),
    ("announcements", {}),
    ("news_acticle", {"url": "some-article"}),
    ("about", {}),
    ("club", {}),
    ("comments", {}),
    ("contact", {}),
    ("pickup", {}),
    ("rules", {}),
    ("weather", {}),
    ("welcome", {}),
    ("youth", {}),
    ("static_page", {"content_url": "foo"}),
    # user
    ("user", {}),
    ("auth_log_in", {}),
    ("auth_log_out", {}),
    ("password_reset", {}),
    ("password_reset_done", {}),
    ("registration_register", {}),
    ("editprofile", {}),
    ("editratings", {}),
    # captain
    ("captain", {}),
    ("captaineditteam", {"team_id": "1"}),
    ("captain_team_export", {"team_id": "1"}),
    ("playersurvey", {"team_id": "1"}),
    ("gamereport", {"team_id": "1", "game_id": "1"}),
    # leagues
    ("league_index_year", {"year": "2026"}),
    ("league_index_season", {"year": "2026", "season": "summer"}),
    ("league_summary", LEAGUE_KWARGS),
    ("league_details", LEAGUE_KWARGS),
    ("league_players", LEAGUE_KWARGS),
    ("league_teams", LEAGUE_KWARGS),
    ("league_group", LEAGUE_KWARGS),
    ("league_registration", LEAGUE_KWARGS),
    ("league_registration_complete", LEAGUE_KWARGS),
    # junta
    ("junta", {}),
    ("concussion_compliance", {}),
    ("captainstatus", {}),
    ("leagueresults", {}),
    ("gamereports", {}),
    ("registrationexport", {}),
    ("schedulegeneration", {}),
    ("teamgeneration", {}),
]


class URLReverseSmokeTest(TestCase):
    def test_all_named_routes_reverse(self):
        failures = []
        for name, kwargs in NAMED_ROUTES:
            try:
                reverse(name, kwargs=kwargs)
            except NoReverseMatch as exc:
                failures.append("{}({}): {}".format(name, kwargs, exc))
        self.assertEqual(failures, [], "named routes failed to reverse:\n" + "\n".join(failures))

    def test_password_reset_confirm_reverses(self):
        user = get_user_model().objects.create_user(
            email="password-reset@example.com", password="test-password"
        )
        token = default_token_generator.make_token(user)

        reverse(
            "password_reset_confirm",
            kwargs={"uidb64": "MQ", "token": token},
        )
