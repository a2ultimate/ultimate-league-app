import csv
from datetime import timedelta
import operator

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader, Context

from ultimate.forms import ScheduleGenerationForm

from ultimate.junta.models import *
from ultimate.leagues.models import *
from ultimate.user.models import *

@login_required
def index(request):

	return render_to_response('junta/index.html',
		{},
		context_instance=RequestContext(request))


@login_required
def captainstatus(request, year=None, season=None, division=None):
	league = None
	leagues = None

	if (year and season and division):
		league = get_object_or_404(League, year=year, season=season, night=division)

	else:
		leagues = League.objects.all().order_by('-league_start_date')

	return render_to_response('junta/captainstatus.html',
		{'league': league, 'leagues': leagues},
		context_instance=RequestContext(request))


@login_required
def registrationexport(request, year=None, season=None, division=None):
	leagues = League.objects.all().order_by('-league_start_date')

	if (year and season and division):
		league = get_object_or_404(League, year=year, season=season, night=division)
		registrations = Registrations.objects.filter(Q(check_complete=1) | Q(paypal_complete=1), league=league, waitlist=0, refunded=0) \
			.extra(select={'average_athletic':'select COALESCE(AVG(skills.athletic), 0) FROM skills WHERE skills.user_id = registrations.user_id AND skills.athletic != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'average_forehand':'select COALESCE(AVG(skills.forehand), 0) FROM skills WHERE skills.user_id = registrations.user_id AND skills.forehand != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'average_backhand':'select COALESCE(AVG(skills.backhand), 0) FROM skills WHERE skills.user_id = registrations.user_id AND skills.backhand != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'average_receive':'select COALESCE(AVG(skills.receive), 0) FROM skills WHERE skills.user_id = registrations.user_id AND skills.receive != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'experience':'select COALESCE(MAX(skills.experience), 0) FROM skills WHERE skills.user_id = registrations.user_id AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'average_strategy':'select COALESCE(AVG(skills.strategy), 0) FROM skills WHERE skills.user_id = registrations.user_id AND skills.strategy != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'average_spirit':'select COALESCE(AVG(skills.spirit), 7) FROM skills WHERE skills.user_id = registrations.user_id AND skills.spirit != 0 AND (skills.not_sure = 0 OR skills.not_sure IS NULL)'}) \
			.extra(select={'highest_level':'select highest_level FROM skills WHERE skills.user_id = registrations.user_id AND skills.user_id = skills.submitted_by_id'})

		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="' + league.__unicode__() + '.txt"'

		# response = HttpResponse()

		t = loader.get_template('junta/registrationexport.txt')
		c = Context({
			'leagues': leagues,
			'registrations': registrations,
		})
		response.write(t.render(c))
		return response

	return render_to_response('junta/registrationexport.html',
		{'leagues': leagues},
		context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def teamimport(request):
	# TODO needs validation
	leagues = League.objects.all().order_by('-league_start_date')

	if request.method == 'POST':
		league = get_object_or_404(League, id=request.POST['league_id'])
		uploadFile = request.FILES['file']

		rows = [row for row in csv.reader(uploadFile.read().splitlines(), dialect='excel-tab')]

		current_team = None
		current_team_count = None
		for row in rows:
			if row[0] != 'Team':
				team_count = row[0]
				email = row[7]
				captain = row[23]
				if team_count not in (None, '') and email not in (None, '') and captain != None:
					if team_count != current_team_count:
						current_team_count = team_count
						current_team = Team()
						current_team.league = league
						current_team.save()
						current_team.name = 'Team ' + str(current_team.id)
						current_team.save()

					team_member = TeamMember()
					team_member.captain = bool(captain)
					team_member.team = current_team
					team_member.user = User.objects.get(email=email)
					team_member.save()

		messages.success(request, 'Teams were successfully imported.')
		return HttpResponseRedirect(reverse('junta'))


	return render_to_response('junta/teamimport.html',
		{'leagues': leagues},
		context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def schedulegeneration(request, year=None, season=None, division=None):
	league = None
	leagues = None
	form = None
	schedule = None
	num_teams = 0

	if (year and season and division):
		league = get_object_or_404(League, year=year, season=season, night=division)
		num_events = league.get_num_game_events()

		schedule = []
		teams = list(Team.objects.filter(league=league))
		num_teams = len(teams)

		teams = teams[0::2] + list(reversed(teams[1::2]))
		teams = teams[:1] + teams[2:] + teams[1:2]

		shift = 0
		for event_num in range(0, num_events):
			teams = teams[:1] + teams[-1:] + teams[1:-1]

			top = teams[:num_teams // 2]
			bottom = list(reversed(teams[num_teams // 2:]))
			games = zip(top, bottom)

			field_shift = (event_num * 2) % (num_teams // 2)
			print field_shift

			games = games[-field_shift:] + games[:-field_shift]

			schedule_teams = [team for game in games for team in sorted(game, key=operator.attrgetter('id'))]
			schedule.append(schedule_teams)

		if request.method == 'POST':
			form = ScheduleGenerationForm(request.POST)
			if form.is_valid() and len(request.POST.getlist('field_names')) >= (num_teams / 2):
				event_date = league.league_start_date
				field_names = request.POST.getlist('field_names')
				for event in schedule:
					for i, team in enumerate(event):
						if (i % 2 == 0):
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


