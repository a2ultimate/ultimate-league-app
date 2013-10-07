from datetime import date
import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter()
def groups_sort(groups):
	groups.sort(key=lambda group: len(group['list']))
	return groups


@register.filter
def time_until_days(value):

	try:
		difference = value - date.today
	except:
		return value

	return difference.days


@register.filter(is_safe=True)
@stringfilter
def smart_title(value):
    """Converts a string into titlecase."""
    """Excludes [a, an, the, and, but, or, for, nor, of]"""
    t = re.sub(r'([a-z])\'([A-Z])', lambda m: m.group(0).lower(), value.title())
    t = re.sub(r'\d([A-Z])', lambda m: m.group(0).lower(), t)
    return re.sub(r'(?i)\s(a|an|and|for|of|the)\b', lambda m: m.group(0).lower(), t)

