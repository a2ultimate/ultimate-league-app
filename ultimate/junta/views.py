import copy
import csv
from datetime import timedelta
from itertools import groupby
from math import floor
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from ultimate.forms import ScheduleGenerationForm

from ultimate.junta.models import *
from ultimate.leagues.models import *
from ultimate.user.models import *

from paypal.standard.ipn.models import PayPalIPN


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='junta').exists())
def index(request):

	return render_to_response('junta/index.html',
		{},
		context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='junta').exists())
def captainstatus(request, year=None, season=None, division=None):
	league = None
	leagues = None

	if year and season and division:
		league = get_object_or_404(League, year=year, season=season, night=division)

	else:
		leagues = League.objects.all().order_by('-league_start_date')

	return render_to_response('junta/captainstatus.html',
		{'league': league, 'leagues': leagues},
		context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='junta').exists())
def leagueresults(request, year=None, season=None, division=None):
	league = None
	field_names = None
	leagues = None
	team_records = None


	if year and season and division:
		league = get_object_or_404(League, year=year, season=season, night=division)
		field_names = league.get_field_names()
		teams = league.get_teams()

		team_records = {}
		for team in teams:
			team_records[team.id] = team.get_record_list()

	else:
		leagues = League.objects.all().order_by('-league_start_date')

	return render_to_response('junta/leagueresults.html',
		{
			'field_names': field_names,
			'league': league,
			'leagues': leagues,
			'team_records': team_records
		},
		context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='junta').exists())
def registrationexport(request, year=None, season=None, division=None):
	leagues = League.objects.all().order_by('-league_start_date')

	if year and season and division:
		league = get_object_or_404(League, year=year, season=season, night=division)

		# TODO need to use better "complete" registration query
		registrations = Registrations.objects.filter(league=league) \
			.extra(select={'average_experience':'SELECT COALESCE(AVG(player_ratings.experience), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.experience != 0'}) \
			.extra(select={'average_strategy':'SELECT COALESCE(AVG(player_ratings.strategy), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.strategy != 0'}) \
			.extra(select={'average_throwing':'SELECT COALESCE(AVG(player_ratings.throwing), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.throwing != 0'}) \
			.extra(select={'average_athleticism':'SELECT COALESCE(AVG(player_ratings.athleticism), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.athleticism != 0'}) \
			.extra(select={'average_competitiveness':'SELECT COALESCE(AVG(player_ratings.competitiveness), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.competitiveness != 0'}) \
			.extra(select={'average_spirit':'SELECT COALESCE(AVG(player_ratings.spirit), 0) FROM player_ratings WHERE player_ratings.user_id = registrations.user_id AND player_ratings.spirit != 0'})


		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="' + league.__unicode__() + '.csv"'

		writer = csv.writer(response)
		writer.writerow([
			'Team',
			'Baggage Id',
			'Captain',
			'Firstname',
			'Lastname',
			'Gender',
			'Email',
			'Rating Total',
			'Experience',
			'Strategy',
			'Throwing',
			'Athleticism',
			'Competitiveness',
			'Spirit',
			'Age',
			'Height Inches',
			'Jersey',
			'Reg Status',
			'PayPal Email',
			'Attendance',
			'Captaining',
		])

		for registration in registrations:
			if registration.is_complete and not registration.waitlist and not registration.refunded:
				try:
					paypal_row = PayPalIPN.objects.filter(invoice=registration.paypal_invoice_id)[:1].get()
				except PayPalIPN.DoesNotExist:
					paypal_row = None

				try:
					registration_profile = registration.user.get_profile()
					gender = registration_profile.gender.encode('ascii', 'ignore')
					jersey_size = registration_profile.jersey_size.encode('ascii', 'ignore')
				except:
					gender = None
					height_inches = None
					jersey_size = None

				team_member_captain = 0
				team_member_models = TeamMember.objects.filter(user=registration.user, team__league=registration.league)
				if team_member_models.count():
					team_member_captain = team_member_models[:1].get().captain

				writer.writerow([
					registration.get_team_id(),
					registration.baggage,
					int(team_member_captain),
					registration.user.first_name,
					registration.user.last_name,
					gender,
					registration.user.email,
					registration.user.rating_total,
					registration.average_experience,
					registration.average_strategy,
					registration.average_throwing,
					registration.average_athleticism,
					registration.average_competitiveness,
					registration.average_spirit,
					int(registration_profile.age),
					int(registration_profile.height_inches),
					jersey_size,
					registration.status.encode('ascii', 'ignore'),
					paypal_row.payer_email.encode('ascii', 'ignore') if paypal_row else paypal_row,
					registration.attendance,
					registration.captain,
				])

		return response

	return render_to_response('junta/registrationexport.html',
		{
			'leagues': leagues
		},
		context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
@user_passes_test(lambda u: u.is_superuser)
def teamgeneration(request, year=None, season=None, division=None):
	if year and season and division:
		league = get_object_or_404(League, year=year, season=season, night=division)
		teams = Team.objects.filter(league=league)
		players = []

		for registration in league.get_complete_registrations():
			players.append({
				'attendance': registration.attendance,
				'baggage_id': registration.baggage.id,
				'rating_total': registration.user.rating_total,
				'team_id': registration.get_team_id(),
				'user': registration.user
			})

		players.sort(key=lambda k: (k['team_id'], k['baggage_id']))

		if request.method == 'POST':
			new_teams = []
			if 'generate_teams' in request.POST:
				num_teams = int(request.POST.get('num_teams', 0))

				if not num_teams:
					messages.error(request, 'You must specify a number of teams greater than zero.')
					return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))

				if teams:
					messages.error(request, 'Teams were not generated. Teams already exist for this league.')
					return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))

				captain_users = {}
				for key in request.POST:
					if key.startswith('player_captain_') and not int(request.POST[key]) == 0:
						captain_users[int(key.split('_').pop())] = int(request.POST[key])

				captain_teams = list(set(captain_users.values()))
				for key in captain_users:
					captain_users[key] = captain_teams.index(captain_users[key])

				groups = list({'baggage_id': k, 'players': sorted(list(v), key=lambda k: k['rating_total'], reverse=True)} for k, v in groupby(players, key=lambda k: k['baggage_id']))

				for group in groups:
					group['attendance_total'] = sum(player['attendance'] for player in group['players'])

					group['rating_total'] = float(sum(player['rating_total'] for player in group['players']))
					group['rating_average'] = group['rating_total'] / len(group['players'])

					group['num_players'] = len(group['players'])
					group['num_females'] = 0
					group['num_males'] = 0

					group['captain'] = None

					for player in group['players']:
						if player['user'].id in [key for key in captain_users]:
							group['captain'] = captain_users[player['user'].id]

						try:
							if player['user'].get_profile().gender == 'F':
								group['num_females'] += 1
							else:
								group['num_males'] += 1
						except ObjectDoesNotExist:
							group['num_males'] += 1

				# goal is something close to LPT, Longest Processing Time

				captain_groups = list(g for g in groups if not g['captain'] == None)
				female_groups = list(g for g in groups if g['num_females'] > 0 and g['captain'] == None)
				male_groups = list(g for g in groups if g['num_females'] <= 0 and g['captain'] == None)

				# sort female and male groups, least important to most important values
				# sort by attendance
				female_groups.sort(key=lambda k: k['attendance_total'])
				male_groups.sort(key=lambda k: k['attendance_total'])
				# sort by total rating of group
				female_groups.sort(key=lambda k: k['rating_average'])
				male_groups.sort(key=lambda k: k['rating_average'])
				# sort by size of group
				female_groups.sort(key=lambda k: k['num_players'], reverse=True)
				male_groups.sort(key=lambda k: k['num_players'], reverse=True)
				# sort female groups by number of females
				female_groups.sort(key=lambda k: k['num_females'], reverse=True)

				# create a team object to track the teams as they are built
				teams_object = list(copy.deepcopy({'num_players': 0, 'num_females': 0, 'num_males': 0, 'rating_total': 0, 'rating_average': 0, 'attendance_total': 0, 'attendance_average': 0, 'groups': [], 'players': []}) for i in range(num_teams))

				# number of players on the biggest team
				team_cap = floor(float(len(players)) / num_teams)

				# add a group to a team and update all team values
				def assign_group_to_team(group, team):
					team['groups'].append(group)
					team['players'].extend(group['players'])

					team['num_players'] += len(group['players'])
					team['num_females'] += group['num_females']
					team['num_males'] += group['num_males']

					team['rating_total'] += group['rating_total']
					team['rating_average'] = team['rating_total'] / team['num_players']

					team['attendance_total'] += group['attendance_total']
					team['attendance_average'] = float(team['attendance_total']) / team['num_players']

				# distribute the groups with captains in them, one per team
				for group in captain_groups:
					if not group['captain'] == None and group['captain'] < num_teams:
						assign_group_to_team(group, teams_object[group['captain']])

				# distribute the groups with females in them, should split females as evenly as possible
				for group in female_groups:
					teams_object.sort(key=lambda k: k['attendance_total'], reverse=True)
					teams_object.sort(key=lambda k: k['rating_average'], reverse=True)
					teams_object.sort(key=lambda k: k['num_females'])
					teams_object.sort(key=lambda k: k['num_players'] + len(group['players']) > team_cap)
					assign_group_to_team(group, teams_object[0])

				# distribute the remaining groups (all male groups)
				for group in male_groups:
					teams_object.sort(key=lambda k: k['attendance_total'], reverse=True)
					teams_object.sort(key=lambda k: k['rating_average'], reverse=True)
					teams_object.sort(key=lambda k: k['num_players'] + len(group['players']) > team_cap)

					if group['rating_average'] > teams_object[0]['rating_average']:
						teams_object.sort(key=lambda k: k['attendance_total'])
						teams_object.sort(key=lambda k: k['rating_average'])
						teams_object.sort(key=lambda k: k['num_players'] + len(group['players']) > team_cap)

					assign_group_to_team(group, teams_object[0])

				# reorganize new teams so that they can be saved
				for team in teams_object:
					new_teams.append({
						'captains': list(User.objects.get(id=user_id) for user_id in captain_users.keys()),
						'team_id': None,
						'users': [player['user'] for player in team['players']]
					})
			elif 'save_teams' in request.POST:
				for key in request.POST:
					team_member_match = re.match(r'^team_member_([\d]+)$', key)
					team_member_captain_match = re.match(r'^team_member_captain_([\d]+)$', key)

					if team_member_match:
						team_id = team_member_match.group(1)
						team = filter(lambda k: k['team_id'] == team_id, new_teams)

						users = list(User.objects.get(id=user_id) for user_id in request.POST.getlist(key))

						if team:
							team[0]['users'] = users
						else:
							new_teams.append({
								'captains': [],
								'team_id': team_id,
								'users': users
							})

					elif team_member_captain_match:
						team_id = team_member_captain_match.group(1)
						team = filter(lambda k: k['team_id'] == team_id, new_teams)

						captains = list(User.objects.get(id=user_id) for user_id in request.POST.getlist(key))

						if team:
							team[0]['captains'] = captains
						else:
							new_teams.append({
								'captains': captains,
								'team_id': team_id,
								'users': []
							})

			if 'publish_teams' in request.POST:
				teams.update(hidden=False)

				messages.success(request, 'Teams were successfully published.')
				return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))

			elif 'hide_teams' in request.POST:
				teams.update(hidden=True)

				messages.success(request, 'Teams were successfully hidden.')
				return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))
			elif 'delete_teams' in request.POST:
				teams.delete()

				messages.success(request, 'Teams were successfully deleted.')
				return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))
			# if POST and no other parameter, need to save newly generated teams
			else:
				for new_team in new_teams:
					team = None
					if new_team['team_id']:
						team = Team.objects.get(id=new_team['team_id'])
					else:
						team = Team()
						team.league = league
						team.hidden = True
						team.save()

					if team:
						for user in new_team['users']:
							try:
								team_member = TeamMember.objects.get(team__league=league, user=user)
							except ObjectDoesNotExist:
								team_member = TeamMember()
								team_member.user = user

							team_member.captain = user in new_team['captains']
							team_member.team = team
							team_member.save()

				messages.success(request, 'Teams were successfully generated.')
				return HttpResponseRedirect(reverse('teamgeneration_league', kwargs={'year': year, 'season':season, 'division': division}))

		response_dictionary = {
			'league': league,
			'teams': teams,
			'players': players
		}


	else:
		leagues = League.objects.all().order_by('-league_start_date')
		response_dictionary = {'leagues': leagues}

	return render_to_response('junta/teamgeneration.html',
		response_dictionary,
		context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
@user_passes_test(lambda u: u.is_superuser)
def schedulegeneration(request, year=None, season=None, division=None):
	league = None
	leagues = None
	form = None
	schedule = None
	num_teams = 0

	if year and season and division:
		league = get_object_or_404(League, year=year, season=season, night=division)
		num_events = league.get_num_game_events()

		schedule = []
		teams = list(Team.objects.filter(league=league))
		num_teams = len(teams)

		if num_teams:
			teams = teams[0::2] + list(reversed(teams[1::2]))
			teams = teams[:1] + teams[2:] + teams[1:2]

			field_shift = 0
			for event_num in range(0, num_events):
				teams = teams[:1] + teams[-1:] + teams[1:-1]

				top = teams[:num_teams // 2]
				bottom = list(reversed(teams[num_teams // 2:]))
				games = zip(top, bottom)

				field_shift = (event_num * 2) % (num_teams // 2)

				games = games[-field_shift:] + games[:-field_shift]

				schedule_teams = [team for game in games for team in sorted(game, key=lambda k: k.id)]
				schedule.append(schedule_teams)

		if request.method == 'POST':
			form = ScheduleGenerationForm(request.POST)
			if form.is_valid() and len(request.POST.getlist('field_names')) >= (num_teams / 2):
				event_date = league.league_start_date
				field_names = request.POST.getlist('field_names')
				for event in schedule:
					for i, team in enumerate(event):
						if i % 2 == 0:
							game = Game()
							game.date = event_date
							game.field_name = FieldNames.objects.get(id=field_names[i / 2])
							game.league = league
							game.save()

						game_team = GameTeams()
						game_team.game = game
						game_team.team = team
						game_team.save()

					event_date = event_date + timedelta(days=7)

				messages.success(request, 'Schedule was successfully generated.')
				return HttpResponseRedirect(reverse('schedulegeneration'))
			else:
				if len(request.POST.getlist('field_names')) >= (num_teams / 2):
					messages.error(request, 'There was an issue with the form you submitted.')
				else:
					messages.error(request, 'You must pick enough fields to cover the number of games for an event.')
		else:
			form = ScheduleGenerationForm()

		form.fields['field_names'].queryset = FieldNames.objects.filter(field__league=league)


	else:
		leagues = League.objects.all().order_by('-league_start_date')

	return render_to_response('junta/schedulegeneration.html',
		{'league': league, 'leagues': leagues, 'form': form, 'schedule': schedule, 'num_games': num_teams / 2},
		context_instance=RequestContext(request))

