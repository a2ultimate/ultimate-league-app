from django import template

register = template.Library()


@register.filter
def get_team_name_font_size(name):
	if len(name) <= 17:
		return 24
	else:
		return 20


@register.filter
def get_game_opponent(game, user):
	try:
		team_name = game.get_user_opponent(user).name
	except AttributeError:
		team_name = 'No Opponent'

	return team_name


# returns average of a column, given a lable and an object/row
@register.filter
def get_average(row, label):
	if row.__dict__['average_' + label.lower()]:
		return '%.1f' % row.__dict__['average_' + label.lower()]
	return 0
