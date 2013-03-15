# -*- coding: utf-8 -*-

import os.path

from django.conf import settings

from pybb.util import filter_blanks, rstrip_str


PYBB_TOPIC_PAGE_SIZE = getattr(settings, 'PYBB_TOPIC_PAGE_SIZE', 10)
PYBB_FORUM_PAGE_SIZE = getattr(settings, 'PYBB_FORUM_PAGE_SIZE', 20)
PYBB_DEFAULT_TIME_ZONE = getattr(settings, 'PYBB_DEFAULT_TIME_ZONE', -5)

PYBB_DEFAULT_MARKUP = getattr(settings, 'PYBB_DEFAULT_MARKUP', 'bbcode')
PYBB_FREEZE_FIRST_POST = getattr(settings, 'PYBB_FREEZE_FIRST_POST', False)

PYBB_DEFAULT_TITLE = getattr(settings, 'PYBB_DEFAULT_TITLE', 'PYBB Powered Forum')

from postmarkup import render_bbcode
from markdown import Markdown

PYBB_MARKUP_ENGINES = getattr(settings, 'PYBB_MARKUP_ENGINES', {
    'bbcode': lambda str: render_bbcode(str, exclude_tags=['size', 'center']),
    'markdown': lambda str: Markdown(safe_mode='escape').convert(str)
})

PYBB_QUOTE_ENGINES = getattr(settings, 'PYBB_QUOTE_ENGINES', {
    'bbcode': lambda text, username="": '[quote="%s"]%s[/quote]\n' % (username, text),
    'markdown': lambda text, username="": '>'+text.replace('\n','\n>').replace('\r','\n>') + '\n'
})

PYBB_MARKUP = getattr(settings, 'PYBB_MARKUP', 'bbcode')
PYBB_BUTTONS = getattr(settings, 'PYBB_BUTTONS', {})
#Dict of buttons that will be used, instead of text links if defined
#Currently supported buttons:
#  new_topic
#  submit
#  save

PYBB_TEMPLATE = getattr(settings, 'PYBB_TEMPLATE', "base.html")
PYBB_ENABLE_ANONYMOUS_POST = getattr(settings, 'PYBB_ENABLE_ANONYMOUS_POST', False)
PYBB_ANONYMOUS_USERNAME = getattr(settings, 'PYBB_ANONYMOUS_USERNAME', 'Anonymous')
PYBB_PREMODERATION = getattr(settings, 'PYBB_PREMODERATION', False)

PYBB_BODY_CLEANERS = getattr(settings, 'PYBB_BODY_CLEANERS', [rstrip_str, filter_blanks])

PYBB_BODY_VALIDATOR = getattr(settings, 'PYBB_BODY_VALIDATOR', None)

PYBB_POLL_MAX_ANSWERS = getattr(settings, 'PYBB_POLL_MAX_ANSWERS', 10)

PYBB_AUTO_USER_PERMISSIONS = getattr(settings, 'PYBB_AUTO_USER_PERMISSIONS', True)

PYBB_USE_DJANGO_MAILER = getattr(settings, 'PYBB_USE_DJANGO_MAILER', False)

PYBB_PERMISSION_HANDLER = getattr(settings, 'PYBB_PERMISSION_HANDLER', 'pybb.permissions.DefaultPermissionHandler')