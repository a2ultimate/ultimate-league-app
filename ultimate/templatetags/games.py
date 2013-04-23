from django import template

register = template.Library()


@register.filter
def get_user_games(league, user):
	return league.get_user_games(user)

@register.filter
def report_complete_for_team(game, user):
	return game.report_complete_for_team(user)

@register.filter
def report_complete_for_user(game, user):
	return game.report_complete_for_user(user)

@register.filter
def get_num_reports_for_user(league, user):
	count = 0
	for game in league.get_user_games(user):
		if game.report_complete_for_user(user):
			count = count + 1

	return count