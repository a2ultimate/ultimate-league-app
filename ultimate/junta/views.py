from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader, Context

from ultimate.junta.models import *
from ultimate.leagues.models import *
from ultimate.user.models import *

@login_required
def index(request):

	return render_to_response('junta/index.html',
		{},
		context_instance=RequestContext(request))

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