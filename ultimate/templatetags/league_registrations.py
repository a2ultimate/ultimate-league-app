from django import template

register = template.Library()


@register.filter
def league_registrations(league, user):
	return league.get_league_registrations_for_user(user)


@register.filter
def get_registration_tick_color(registration, threshold):
	if registration.get_progress() >= threshold:
		return 'success'
	return ''
