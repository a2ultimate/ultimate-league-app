import collections
import re

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.utils import timezone

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, '')

@register.filter()
def groups_sort(groups):
    return sorted(groups, key=lambda group: len(group['list']))


@register.filter(is_safe=True)
@stringfilter
def smart_title(value):
    """Converts a string into titlecase."""
    """Excludes [a, an, the, and, but, or, for, nor, of]"""
    t = re.sub(r'([a-z])\'([A-Z])', lambda m: m.group(0).lower(), value.title())
    t = re.sub(r'\d([A-Z])', lambda m: m.group(0).lower(), t)
    return re.sub(r'(?i)\s(a|an|and|for|of|the)\b', lambda m: m.group(0).lower(), t)


@register.filter(is_safe=True)
def prepare_menu_items(menu_items):
    # credit: http://stackoverflow.com/questions/5059401/make-a-python-nested-list-for-use-in-djangos-unordered-list

    from ultimate.index.models import StaticMenuItems

    lists = collections.defaultdict(list)
    for menu_item in menu_items:
        itemHtml = ''

        if menu_item.type == 'external_link':
            itemHtml += '<a href="' + menu_item.href + '" target="_blank">'
        elif menu_item.type == 'internal_link':
            itemHtml += '<a href="' + reverse(menu_item.href) + '">'
        elif menu_item.type == 'static_link':
            itemHtml += '<a href="' + settings.STATIC_URL + menu_item.href + '">'
        elif menu_item.type == 'header':
            itemHtml += '<h2>'

        itemHtml += menu_item.content

        if menu_item.type == 'external_link' or \
                menu_item.type == 'internal_link' or \
                menu_item.type == 'static_link':

            itemHtml += '</a>'
        elif menu_item.type == 'header':
            itemHtml += '</h2>'

        parent_id = 0

        try:
            if menu_item.parent:
                parent_id = menu_item.parent_id
        except StaticMenuItems.DoesNotExist:
            pass

        lists[parent_id] += [itemHtml, lists[menu_item.id]]

    for menu_item in menu_items:
        if not lists[menu_item.id]:
            parent_id = 0

            try:
                if menu_item.parent:
                    parent_id = menu_item.parent_id
            except StaticMenuItems.DoesNotExist:
                pass

            lists[parent_id].remove(lists[menu_item.id])

    return lists[0]
