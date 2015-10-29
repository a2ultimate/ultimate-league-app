# -*- coding: utf-8 -*-

from pybb import defaults

__author__ = 'zeus'


def processor(request):
    context = {}
    for i in (
        'PYBB_TEMPLATE',
        'PYBB_MARKUP',
        'PYBB_DEFAULT_TITLE',
        'PYBB_ENABLE_ANONYMOUS_POST'
        ):
        context[i] = getattr(defaults, i, None)
    return context
