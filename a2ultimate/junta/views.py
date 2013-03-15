from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from a2ultimate.junta.models import *
from a2ultimate.leagues.models import *
from a2ultimate.user.models import *

@login_required
def index(request):

	return render_to_response('junta/index.html',
		{},
		context_instance=RequestContext(request))