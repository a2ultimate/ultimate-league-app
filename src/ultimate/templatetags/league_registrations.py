from django import template

register = template.Library()


@register.filter
def league_registrations(league, user):
    return league.get_registrations_for_user(user)


@register.filter
def get_registration_tick_color(threshold, registration):
    if registration.progress >= threshold:
        return 'success'

    return ''
