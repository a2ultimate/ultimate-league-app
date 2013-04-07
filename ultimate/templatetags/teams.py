from django import template

register = template.Library()

@register.filter
def get_team(team, index):
	return team[index].team

@register.filter
def get_team_id(team, index):
	return team[index].team.id

@register.filter
def get_team_name(team, index):
	return team[index].team.name

@register.filter
def get_team_color(team, index):
	return team[index].team.color

@register.filter
def get_field_game_teams(games, field_name):
	for i, game in enumerate(games):
		if game.field_name == field_name:
			del games[i]
			return game.get_teams()
	return None

@register.filter
def get_team_name_font_size(name):
	if len(name) <= 14:
		return 24
	# elif len(name) <= 17:
	# 	return 21
	else:
		return 21

@register.filter
def num_spots_left(league, group):
	return int(league.baggage) - int(len(group))

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

