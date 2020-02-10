from django import template

register = template.Library()



@register.filter
def is_on_team(user, team):
    return team.contains_user(user)


@register.filter
def get_game_opponent_team(game, user):
    try:
        return game.get_user_opponent(user)
    except AttributeError:
        pass

    return None


@register.filter
def get_game_opponent_team_name(game, user):
    try:
        if game.get_user_opponent(user).name:
            return game.get_user_opponent(user).name
        else:
            return 'Team {}'.format(game.get_user_opponent(user).id)
    except AttributeError:
        pass

    return 'No Opponent'


# returns average of a column, given a lable and an object/row
@register.filter
def get_average(row, label):
    if row.__dict__['average_' + label.lower()]:
        return '{:.1f}'.format(row.__dict__['average_' + label.lower()])
    return 0
