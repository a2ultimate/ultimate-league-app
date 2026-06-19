"""Minimal object factories for the leagues test suite.

These build just enough of the object graph (User -> Season -> League ->
Team -> TeamMember) to exercise the email-group sync paths, filling required
model fields with sane defaults so individual tests only specify what they
care about.
"""

from datetime import date, datetime

from django.contrib.auth import get_user_model

from ultimate.leagues.models import League, Season, Team, TeamMember

User = get_user_model()


def make_user(email, first_name="Test", last_name="User"):
    return User.objects.create_user(
        email=email, first_name=first_name, last_name=last_name
    )


def make_season(slug, name=None, order=0):
    # Season.save() is overridden without *args/**kwargs, so objects.create()
    # (which passes force_insert=) fails; build and save the instance directly.
    season = Season(slug=slug, name=name or slug.replace("-", " ").title(), order=order)
    season.save()
    return season


def make_league(season, year, **overrides):
    """Create a League with all required fields defaulted.

    Only season and year matter for the email-group tests; everything else is
    boilerplate the model requires to save.
    """
    dt = datetime(year, 1, 1, 12, 0, 0)
    defaults = dict(
        season=season,
        year=year,
        night="sunday",
        night_slug="sunday",
        gender=League.LEAGUE_GENDER_COREC,
        level=League.LEAGUE_LEVEL_RECREATIONAL,
        type=League.LEAGUE_TYPE_LEAGUE,
        summary_info="",
        detailed_info="",
        times="6:00-8:00pm",
        reg_start_date=dt,
        price_increase_start_date=dt,
        group_lock_start_date=dt,
        waitlist_start_date=dt,
        league_start_date=date(year, 1, 1),
        league_end_date=date(year, 3, 1),
        max_players=100,
        baggage=2,
        paypal_cost=50,
        check_cost_increase=5,
        late_cost_increase=5,
        mail_check_address="",
        state=League.LEAGUE_STATE_CLOSED,
    )
    defaults.update(overrides)
    # League.save() is also overridden without *args/**kwargs (see make_season).
    league = League(**defaults)
    league.save()
    return league


def make_team(league, name="Team"):
    return Team.objects.create(league=league, name=name)


def make_team_member(team, user, captain=False):
    return TeamMember.objects.create(team=team, user=user, captain=captain)


def add_player(team, email, captain=False, first_name="Test", last_name="User"):
    """Convenience: create a user and attach them to a team in one call."""
    user = make_user(email, first_name=first_name, last_name=last_name)
    return make_team_member(team, user, captain=captain)
