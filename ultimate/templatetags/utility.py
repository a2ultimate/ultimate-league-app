from django import template

from datetime import date

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