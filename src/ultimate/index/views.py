from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from pybb.models import Topic

from ultimate.index.models import *
from ultimate.forms import AnnoucementsForm
from ultimate.utils.calendar import get_events
from ultimate.utils.email_groups import add_to_group


def index(request):
    announcements = Topic.objects.filter(
        forum__name__exact='Announcements').order_by('-created')[:5]

    events = get_events()[:8]

    return render_to_response('index/index.html',
                              {
                                  'announcements': announcements,
                                  'events': events,
                              },
                              context_instance=RequestContext(request))


def announcements(request):
    if request.method == 'POST':
        form = AnnoucementsForm(request.POST)
        user_email_address = request.POST.get('email', False)
        group_email_address = getattr(
            settings, 'ANNOUNCEMENTS_GROUP_ADDRESS', False)

        if form.is_valid() and user_email_address and group_email_address:
            success_count = add_to_group(
                group_email_address=group_email_address,
                email_address=user_email_address)

            if success_count:
	            messages.success(
	                request, 'Your email address was added successfully.')
	            return HttpResponseRedirect(reverse('announcements'))
            else:
                messages.error(
                    request, 'Your email address could not be added. It is possible that you are already a member.')

        else:
            messages.error(
                request, 'There was an error on the form you submitted.')
    else:
        form = AnnoucementsForm()

    return render_to_response('index/announcements.html',
                              {
                                  'form': form,
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
