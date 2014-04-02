from datetime import datetime
from django import template

register = template.Library()


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
	return bool(datetime.now() > league_date)


@register.filter
def is_free(league):
	return bool(league.check_price == 0 and league.paypal_price == 0)


@register.filter
# returns league captains as user objects
def get_league_captains(league):
	return league.get_league_captains()


@register.filter
# returns league captains as teammember objects
def get_league_captains_teammember(league):
	return league.get_league_captains_teammember()


@register.filter
# returns whether a user has filled out a player survey for a league
def get_player_survey_status(league, user):
	return league.player_survey_complete_for_user(user)
