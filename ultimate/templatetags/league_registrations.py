from django import template

from ultimate.leagues.models import REGISTRATION_STATUS_CHOICES

register = template.Library()

@register.filter
def league_registrations(league, user):
	return league.get_league_registrations_for_user(user)