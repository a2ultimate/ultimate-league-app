from django import template

register = template.Library()

@register.filter
def get_team_name_font_size(name):
	if len(name) <= 17:
		return 24
	else:
		return 20

@register.filter
def get_league_teamid(league_games, user):
	return league_games['list'][0].get_user_team(user).id

@register.filter
def get_league_teamname(league_games, user):
	return league_games['list'][0].get_user_team(user).name

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

# returns id of team that user is on for a given game
@register.filter
def get_game_user_teamid(game, user):
	return game.get_user_team(user).id

# returns name of team that user is on for a given game
@register.filter
def get_game_user_teamname(game, user):
	return game.get_user_team(user).name

