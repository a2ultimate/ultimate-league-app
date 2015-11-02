# -*- coding: utf-8 -*-

import math
import time

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils import dateformat

try:
    from django.utils.timezone import timedelta
    from django.utils.timezone import now as tznow
except ImportError:
    import datetime
    from datetime import timedelta
    tznow = datetime.datetime.now

from pybb.models import PollAnswerUser
from pybb.permissions import perms
from pybb import defaults


register = template.Library()


#noinspection PyUnusedLocal
@register.tag
def pybb_time(parser, token):
    try:
        tag, context_time = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('pybb_time requires single argument')
    else:
        return PybbTimeNode(context_time)


class PybbTimeNode(template.Node):
    def __init__(self, time):
    #noinspection PyRedeclaration
        self.time = template.Variable(time)

    def render(self, context):
        context_time = self.time.resolve(context)

        delta = tznow() - context_time
        today = tznow().replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        if delta.days == 0:
            if delta.seconds < 60:
                msg = _('seconds ago')
                return u'%d %s' % (delta.seconds, msg)

            elif delta.seconds < 3600:
                minutes = int(delta.seconds / 60)
                msg = _('minutes ago')
                return u'%d %s' % (minutes, msg)
        if context['user'].is_authenticated():
            if time.daylight:
                tz1 = time.altzone
            else:
                tz1 = time.timezone
            tz = tz1 + getattr(settings, 'PYBB_DEFAULT_TIME_ZONE', 0) * 60 * 60
            context_time = context_time + timedelta(seconds=tz)
        if today < context_time < tomorrow:
            return _('today, %s') % context_time.strftime('%H:%M')
        elif yesterday < context_time < today:
            return _('yesterday, %s') % context_time.strftime('%H:%M')
        else:
            return dateformat.format(context_time, 'd M, Y H:i')


@register.simple_tag
def pybb_link(object, anchor=u''):
    """
    Return A tag with link to object.
    """

    url = hasattr(object, 'get_absolute_url') and object.get_absolute_url() or None
    #noinspection PyRedeclaration
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.filter
def pybb_topic_moderated_by(topic, user):
    """
    Check if user is moderator of topic's forum.
    """

    return perms.may_moderate_topic(user, topic)

@register.filter
def pybb_editable_by(post, user):
    """
    Check if the post could be edited by the user.
    """
    return perms.may_edit_post(user, post)


@register.filter
def pybb_posted_by(post, user):
    """
    Check if the post is writed by the user.
    """
    return post.user == user


@register.filter
def pybb_topic_inline_pagination(topic):
    page_count = int(math.ceil(topic.post_count / float(defaults.PYBB_TOPIC_PAGE_SIZE)))
    if page_count <= 5:
        return range(1, page_count+1)
    return range(1, 5) + ['...', page_count]


@register.filter
def pybb_topic_poll_not_voted(topic, user):
    return not PollAnswerUser.objects.filter(poll_answer__topic=topic, user=user).exists()


@register.filter
def endswith(str, substr):
    return str.endswith(substr)