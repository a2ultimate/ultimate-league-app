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
	return game.get_user_opponent(user).name

#returns whether a user has filled out a player survey for a league
@register.filter
def player_survey_complete(game, user):
	return league_games['list'][0].get_user_team(user).player_survey_complete(user)

# returns average for a skill
@register.filter
def get_average(row, label):
	if row.__dict__['average_' + label.lower()]:
		return '%.1f' % row.__dict__['average_' + label.lower()]
	return 0
