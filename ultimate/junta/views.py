from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

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
	schedule = None

	if (year and season and division):
		league = get_object_or_404(League, year=year, season=season, night=division)

		try:
			schedule = Schedule.objects.get(league=league)
		except Schedule.DoesNotExist:
			schedule = None

	else:
		leagues = League.objects.all().order_by('-league_start_date')

	return render_to_response('junta/captainstatus.html',
		{'league': league, 'schedule': schedule, 'leagues': leagues},
		context_instance=RequestContext(request))