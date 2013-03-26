from django import template

register = template.Library()


@register.filter
def report_complete_for_user(game, user):
	return game.report_complete_for_user(user)
