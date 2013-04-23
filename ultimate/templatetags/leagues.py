from datetime import date
from django import template

register = template.Library()


@register.filter
def is_past_deadline(league_date):
	return bool(date.today() > league_date)


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