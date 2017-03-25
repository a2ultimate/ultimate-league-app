from django import template
from django.utils import timezone

from ultimate.leagues.models import League

register = template.Library()


@register.filter
def sort_by_league_start_date_weekday(divisions):

    leagues = filter(lambda k: k.type == League.LEAGUE_TYPE_LEAGUE, divisions)
    leagues.sort(key=lambda k: k.league_start_date.strftime('%w'))

    other_divisions = filter(lambda k: k.type != League.LEAGUE_TYPE_LEAGUE, divisions)
    other_divisions.sort(key=lambda k: k.league_start_date)

    return leagues + other_divisions


@register.filter
def is_visible(league, user):
    return league.is_visible(user)


@register.filter
def is_open(league, user):
    return league.is_open(user)


@register.filter
def is_waitlist(league, user):
    return league.is_waitlist(user)


@register.filter
def is_past_deadline(league_date):
    return bool(timezone.now() > league_date)


@register.filter
def is_free(league):
    return bool(league.check_price == 0 and league.paypal_price == 0)


@register.filter
def is_accepting_registrations(league, user):
    return league.is_accepting_registrations(user)


@register.filter
def is_waitlisting_registrations(league, user):
    return league.is_waitlisting_registrations(user)


@register.filter
def has_user_registration(league, user):
    return league.get_user_registration(user) is not None


@register.filter
def has_complete_user_registration(league, user):
    user_registration = league.get_user_registration(user)
    return user_registration and \
        user_registration.is_complete


@register.filter
# returns league captains as user objects
def get_captains(league):
    return league.get_captains()


@register.filter
# returns league captains as teammember objects
def get_captains_teammember(league):
    return league.get_captains_teammember()


@register.filter
# returns whether a user has filled out a player survey for a league
def get_player_survey_status(league, user):
    return league.player_survey_complete_for_user(user)
