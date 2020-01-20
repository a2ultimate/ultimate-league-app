import csv
import re
from functools import reduce

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.transaction import atomic
from django.forms.formsets import formset_factory
from django.forms.models import model_to_dict, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone

from ultimate.captain.models import GameReport, GameReportAttendance, GameReportComment, GameReportScore
from ultimate.forms import EditTeamInformationForm, GameReportCommentForm, GameReportScoreForm, PlayerSurveyForm
from ultimate.leagues.models import Game, Registrations, Team, TeamMember
from ultimate.middleware.http import Http403
from ultimate.user.models import PlayerRatings, PlayerRatingsReport


@login_required
def index(request):
    captain_teams = Team.objects.filter(teammember__user=request.user, teammember__captain=True, hidden=False).order_by('-league__league_start_date')

    return render(request, 'captain/index.html',
        {'captain_teams': captain_teams})


@login_required
def editteam(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not bool(team.teammember_set.filter(user=request.user, captain=True)[0:1].count()):
        raise Http403

    if request.method == 'POST':
        form = EditTeamInformationForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your team information was updated successfully.')
            return HttpResponseRedirect(reverse('captaineditteam', kwargs={'team_id': team.id}))
        else:
            messages.error(request, 'There was an error on the form you submitted.')
    else:
        form = EditTeamInformationForm(instance=team)

    return render(request, 'captain/editteam.html',
        {'team': team, 'form': form})


@login_required
def exportteam(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not bool(team.teammember_set.filter(user=request.user, captain=True)[0:1].count()):
        raise Http403

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(team)

    writer = csv.writer(response)
    writer.writerow([
        'Team',
        'Captain',
        'Firstname',
        'Lastname',
        'Email',
        'Gender',
        'Age',
        'Height Inches',
        'Number of Teams',
        'Estimated Absences',
    ])

    team_members = team.teammember_set.all()

    for team_member in team_members:
        try:
            profile = reduce(getattr, 'user.profile'.split('.'), team_member)

            gender = profile.gender
            height_inches = profile.height_inches
            age_on_start_date = profile.get_age_on(team.league.league_start_date)
        except AttributeError:
            gender = None
            age_on_start_date = 0
            height_inches = 0

        writer.writerow([
            int(team.id),
            int(team_member.captain),
            team_member.user.first_name,
            team_member.user.last_name,
            team_member.user.email,
            gender,
            int(0 if age_on_start_date is None else age_on_start_date),
            height_inches,
            TeamMember.objects.filter(user=team_member.user).count(),
            getattr(Registrations.objects.get(user=team_member.user, league=team.league), 'attendance', 0),
        ])

    return response


@atomic
@login_required
def playersurvey(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not bool(team.teammember_set.filter(user=request.user, captain=True)[0:1].count()):
        raise Http403

    team_member_users = get_user_model().objects.filter(teammember__team=team).exclude(id=request.user.id) \
        .extra(select={'average_experience': 'SELECT COALESCE(AVG(user_playerratings.experience), 0) FROM user_playerratings WHERE user_playerratings.user_id = user_user.id AND user_playerratings.experience != 0'}) \
        .extra(select={'average_strategy': 'SELECT COALESCE(AVG(user_playerratings.strategy), 0) FROM user_playerratings WHERE user_playerratings.user_id = user_user.id AND user_playerratings.strategy != 0'}) \
        .extra(select={'average_throwing': 'SELECT COALESCE(AVG(user_playerratings.throwing), 0) FROM user_playerratings WHERE user_playerratings.user_id = user_user.id AND user_playerratings.throwing != 0'}) \
        .extra(select={'average_athleticism': 'SELECT COALESCE(AVG(user_playerratings.athleticism), 0) FROM user_playerratings WHERE user_playerratings.user_id = user_user.id AND user_playerratings.athleticism != 0'}) \
        .extra(select={'average_spirit': 'SELECT COALESCE(AVG(user_playerratings.spirit), 0) FROM user_playerratings WHERE user_playerratings.user_id = user_user.id AND user_playerratings.spirit != 0'}) \
        .distinct()

    try:
        ratings_report, created = PlayerRatingsReport.objects.get_or_create(submitted_by=request.user, team=team,
            defaults={'submitted_by': request.user, 'team': team, 'updated': timezone.now()})
    except IntegrityError:
        ratings_report = PlayerRatingsReport.objects.get(submitted_by=request.user, team=team)

    ratings_form_set = formset_factory(PlayerSurveyForm, extra=0)

    if request.method == 'POST':
        formset = ratings_form_set(request.POST)

        if formset.is_valid():
            for rating_data in formset.cleaned_data:
                user_data = {
                    'ratings_report': ratings_report,
                    'ratings_type': PlayerRatings.RATING_TYPE_CAPTAIN,
                    'submitted_by': request.user,
                    'updated': timezone.now(),
                    'user': team_member_users.get(id=rating_data['user_id'])
                }

                if rating_data['not_sure']:
                    data = {'not_sure': True}
                    data = dict(list(data.items()) + list(user_data.items()))
                else:
                    data = dict(list(rating_data.items()) + list(user_data.items()))
                    del data['user_id']

                ratings_row, created = PlayerRatings.objects.get_or_create(ratings_report=ratings_report, user=data['user'], defaults=data)
                if not created:
                    ratings_row.__dict__.update(data)
                    ratings_row.save()

            messages.success(request, 'Your player survey was updated successfully.')
            return HttpResponseRedirect(reverse('playersurvey', kwargs={'team_id': team_id}))
        else:
            messages.error(request, 'There was an error on the form you submitted.')

    else:
        ratings = []
        for team_member_user in team_member_users:
            try:
                last_rating = model_to_dict(team_member_user.playerratings_set.filter(submitted_by=request.user).order_by('-updated')[0:1].get())
                last_rating['user_id'] = last_rating['user']
            except PlayerRatings.DoesNotExist:
                last_rating = {'user_id': team_member_user.id}
            ratings.append(last_rating)

        formset = ratings_form_set(initial=ratings)

    survey = []
    for (i, form) in enumerate(formset.forms):
        survey.append({
            'user': team_member_users[i],
            'form': form
        })

    return render(request, 'captain/playersurvey.html',
        {
            'formset': formset,
            'ratings_choices': {
                'strategy': PlayerRatings.RATING_STRATEGY_CHOICES,
                'throwing': PlayerRatings.RATING_THROWING_CHOICES,
                'athleticism': PlayerRatings.RATING_ATHLETICISM_CHOICES,
            },
            'survey': survey,
            'team': team
        })


@login_required
@atomic
def gamereport(request, team_id, game_id):
    team = get_object_or_404(Team, id=team_id)
    game = get_object_or_404(Game, id=game_id)

    if not bool(team.teammember_set.filter(user=request.user, captain=True)[0:1].count()) or \
            not bool(game.gameteams_set.filter(team__teammember__user=request.user, team__teammember__captain=True)[0:1].count()):

        raise Http403

    try:
        game_report = GameReport.objects.get(team__id=team_id, game__id=game_id)

        try:
            game_report_comment = GameReportComment.objects.get(report=game_report, submitted_by=request.user)
        except GameReportComment.DoesNotExist:
            game_report_comment = None
    except GameReport.DoesNotExist:
        game_report = None
        game_report_comment = None

    attendance = []
    score_formset_factory = modelformset_factory(GameReportScore, form=GameReportScoreForm, extra=2, max_num=2)

    if request.method == 'POST':

        comment_form = GameReportCommentForm(request.POST, instance=game_report_comment)
        score_formset = score_formset_factory(request.POST)
        for form in score_formset.forms:
            form.empty_permitted = False

        for post_param in request.POST:
            if re.match('user_', post_param):
                attendance.append(int(re.split('user_', post_param)[1]))

        if timezone.now().date() < game.date:
            score_us_form = score_formset.forms[0]
            score_them_form = score_formset.forms[1]
            messages.error(request, 'You cannot submit a game report before the game date.')

        elif not comment_form.is_valid() or not score_formset.is_valid():
            score_us_form = score_formset.forms[0]
            score_them_form = score_formset.forms[1]
            messages.error(request, 'There was an error on the form you submitted.')

        else:
            if game_report:
                game_report.last_updated_by = request.user
            else:
                game_report = GameReport(game=game, team=team, last_updated_by=request.user)
            game_report.save()

            score_us_form = score_formset.forms[0]
            score_them_form = score_formset.forms[1]

            comment = comment_form.save(commit=False)
            comment.report_id = game_report.id
            comment.submitted_by = request.user
            comment.save()

            score_us = score_us_form.save(commit=False)
            score_us.report_id = game_report.id
            score_us.save()

            score_them = score_them_form.save(commit=False)
            score_them.report_id = game_report.id
            score_them.save()

            GameReportAttendance.objects.filter(report=game_report).delete()
            for user_id in attendance:
                attendance_record = GameReportAttendance(report=game_report, user_id=user_id)
                attendance_record.save()

            messages.success(request, 'Your game report was updated successfully.')
            return HttpResponseRedirect(reverse('gamereport', kwargs={'game_id': game_id, 'team_id': team_id}))

    else:
        comment_form = GameReportCommentForm(instance=game_report_comment)
        if game_report:
            for attendance_record in GameReportAttendance.objects.filter(report=game_report):
                attendance.append(attendance_record.user.id)
            score_formset = score_formset_factory(queryset=GameReportScore.objects.filter(report=game_report))
        else:
            game_teams = game.gameteams_set
            user_team = game_teams.filter(team=team).get().team
            opponent_team = game_teams.exclude(team=team).get().team
            score_formset = score_formset_factory(queryset=GameReportScore.objects.none(),
                initial=[{'team': user_team}, {'team': opponent_team}])

        score_us_form = score_formset.forms[0]
        score_them_form = score_formset.forms[1]

    return render(request, 'captain/gamereport.html',
        {
            'game_report': game_report,
            'game': game,
            'team': team,
            'attendance': attendance,
            'comment_form': comment_form,
            'score_formset': score_formset,
            'score_us_form': score_us_form,
            'score_them_form': score_them_form
        })
