from django import template
from ultimate.captain.models import GameReportScore

register = template.Library()


@register.filter
def get_user_games(league, user):
    return league.get_user_games(user)


@register.filter
def get_report_for_team(game, team):
    return game.get_report_for_team(team)


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


@register.filter
def get_result(report, team):
    homeReportScore = report.gamereportscore_set.filter(team=team)[0]
    awayReportScore = report.gamereportscore_set.exclude(team=team)[0]

    if homeReportScore.score > awayReportScore.score:
        return 'win'
    elif homeReportScore.score < awayReportScore.score:
        return 'loss'
    return 'tie'


@register.filter
def get_report_scores_formatted(report):
    return '%d - %d' % (report.gamereportscore_set.all()[0].score, report.gamereportscore_set.all()[1].score)
