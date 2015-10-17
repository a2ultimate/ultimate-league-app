from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from pybb.models import Topic

from ultimate.index.models import *

import feedparser

def index(request):
	announcements = Topic.objects.filter(forum__name__exact='Announcements').order_by('-created')[:5]

	return render_to_response('index/index.html',
		{
			'announcements': announcements,
		},
		context_instance=RequestContext(request))

def content(request, url):
	try:
		content = get_object_or_404(StaticContent, url=url)
	except StaticContent.DoesNotExist:
		content = ''
	return render_to_response('index/content.html',
		{'content': content},
		context_instance=RequestContext(request))
