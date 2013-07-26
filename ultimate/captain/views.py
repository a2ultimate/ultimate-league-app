from datetime import datetime
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Avg, Q
from django.forms.formsets import formset_factory
from django.forms.models import model_to_dict, modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from ultimate.captain.models import *
from ultimate.user.models import *
from ultimate.forms import *
from ultimate.middleware.http import Http403

@login_required
def index(request):
	captain_teams = Team.objects.filter(teammember__user=request.user, teammember__captain=1).order_by('-league__league_start_date')

	return render_to_response('captain/index.html',
		{'captain_teams': captain_teams},
		context_instance=RequestContext(request))

@login_required
def editteam(request, teamid):
	team = get_object_or_404(Team, id=teamid)

	if not bool(team.teammember_set.filter(user=request.user,captain=1)[0:1].count()):
		raise Http403

	if request.method == 'POST':
		form = EditTeamInformationForm(request.POST, instance=team)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your team information was updated successfully.')
			return HttpResponseRedirect(reverse('captaineditteam', kwargs={'teamid':team.id}))
		else:
			messages.error(request, 'There was an error on the form you submitted.')
	else:
		form = EditTeamInformationForm(instance=team)

	return render_to_response('captain/editteam.html',
		{'team': team, 'form': form},
		context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def playersurvey(request, teamid):
	team = get_object_or_404(Team, id=teamid)

	if not bool(team.teammember_set.filter(user=request.user,captain=1)[0:1].count()):
		raise Http403

	team_member_users = User.objects.filter(teammember__team=team).exclude(id=request.user.id) \
		.extra(select={'average_athletic':'select AVG(skills.athletic) FROM skills WHERE skills.user_id = auth_user.id AND skills.athletic != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.extra(select={'average_forehand':'select AVG(skills.forehand) FROM skills WHERE skills.user_id = auth_user.id AND skills.forehand != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.extra(select={'average_backhand':'select AVG(skills.backhand) FROM skills WHERE skills.user_id = auth_user.id AND skills.backhand != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.extra(select={'average_receive':'select AVG(skills.receive) FROM skills WHERE skills.user_id = auth_user.id AND skills.receive != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.extra(select={'average_strategy':'select AVG(skills.strategy) FROM skills WHERE skills.user_id = auth_user.id AND skills.strategy != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.extra(select={'average_spirit':'select AVG(skills.spirit) FROM skills WHERE skills.user_id = auth_user.id AND skills.spirit != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
		.distinct()

	skills_report, created = SkillsReport.objects.get_or_create(submitted_by=request.user, team=team,
		defaults={'updated': datetime.now()})
	skills_type = SkillsType.objects.get(id=3)

	SkillFormSet = formset_factory(PlayerSurveyForm, extra=0)

	if request.method == 'POST':
		formset = SkillFormSet(request.POST)

		if formset.is_valid():
			for skill_data in formset.cleaned_data:
				skill_user = team_member_users.get(id=skill_data['user_id'])
				user_data = {'user': skill_user, 'skills_report': skills_report, 'submitted_by': request.user, 'skills_type': skills_type, 'updated': datetime.now()}

				if not skill_data['not_sure']:
					data = dict(skill_data.items() + user_data.items())
					del data['user_id']

					skills_row, created = Skills.objects.get_or_create(skills_report=skills_report, user=skill_user, defaults=data)
					if not created:
						skills_row.__dict__.update(data)
						skills_row.save()
				else:
					data = {'not_sure': True}
					data =  dict(data.items() + user_data.items())
					skills_row, created = Skills.objects.get_or_create(skills_report=skills_report, user=skill_user, defaults=data)
					if not created:
						skills_row.__dict__.update(data)
						skills_row.save()

			messages.success(request, 'Your player survey was updated successfully.')
			return HttpResponseRedirect(reverse('playersurvey', kwargs={'teamid':teamid}))
		else:
			messages.error(request, 'There was an error on the form you submitted.')

	else:
		skills = []
		for team_member_user in team_member_users:
			try:
				last_skill = model_to_dict(team_member_user.skills_set.filter(submitted_by=request.user).order_by('-updated')[0:1].get())
				last_skill['user_id'] = last_skill['user']
			except Skills.DoesNotExist:
				last_skill = {'user_id': team_member_user.id}
			skills.append(last_skill)
		formset = SkillFormSet(initial=skills)

	survey = []
	for (i, form) in enumerate(formset.forms):
		survey.append({
			'user': team_member_users[i],
			'form': form})

	return render_to_response('captain/playersurvey.html',
		{'team': team, 'formset': formset, 'survey': survey},
		context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def gamereport(request, teamid, gameid):
	team = get_object_or_404(Team, id=teamid)
	game = get_object_or_404(Game, id=gameid)

	if not bool(team.teammember_set.filter(user=request.user,captain=1)[0:1].count()) or \
		not bool(game.gameteams_set.filter(team__teammember__user=request.user, team__teammember__captain=1)[0:1].count()):

		raise Http403

	try:
		game_report = GameReport.objects.get(team__id=teamid, game__id=gameid)

		try:
			game_report_comment = GameReportComment.objects.get(report=game_report, submitted_by=request.user)
		except GameReportComment.DoesNotExist:
			game_report_comment = None
	except GameReport.DoesNotExist:
		game_report = None
		game_report_comment = None

	attendance = []
	ScoreFormset = modelformset_factory(GameReportScore, form=GameReportScoreForm, extra=2, max_num=2)

	if request.method == 'POST':

		comment_form = GameReportCommentForm(request.POST, instance=game_report_comment)
		score_formset = ScoreFormset(request.POST)
		for form in score_formset.forms:
			form.empty_permitted = False

		for postParam in request.POST:
			if re.match('user_', postParam):
				attendance.append(int(re.split('user_', postParam)[1]))

		if comment_form.is_valid() and score_formset.is_valid():

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
				attendanceRecord = GameReportAttendance(report=game_report, user_id=user_id)
				attendanceRecord.save()

			messages.success(request, 'Your game report was updated successfully.')
			return HttpResponseRedirect(reverse('gamereport', kwargs={'gameid':gameid, 'teamid':teamid}))
		else:
			score_us_form = score_formset.forms[0]
			score_them_form = score_formset.forms[1]
			messages.error(request, 'There was an error on the form you submitted.')

	else:
		comment_form = GameReportCommentForm(instance=game_report_comment)
		if game_report:
			for attendanceRecord in GameReportAttendance.objects.filter(report=game_report):
				attendance.append(attendanceRecord.user.id)
			score_formset = ScoreFormset(queryset=GameReportScore.objects.filter(report=game_report))
		else:
			game_teams = game.gameteams_set
			score_formset = ScoreFormset(queryset=GameReportScore.objects.none(),
				initial=[{'team': game_teams.filter(team=team).get().team}, {'team': game_teams.exclude(team=team).get().team},])

		score_us_form = score_formset.forms[0]
		score_them_form = score_formset.forms[1]

	return render_to_response('captain/gamereport.html',
		{'game_report': game_report, 'game': game, 'team': team,
			'attendance': attendance,
			'comment_form': comment_form,
			'score_formset': score_formset,
			'score_us_form': score_us_form,
			'score_them_form': score_them_form},
		context_instance=RequestContext(request))
