from django import template
register = template.Library()

from a2ultimate.leagues.models import TeamMember

@register.filter
def in_group(user, groups):
	# {% if user|in_group:"Friends,Enemies" %}

	group_list = groups.split(',')
	return bool(user.groups.filter(name__in=group_list).values('name'))

@register.filter
def is_captain(user):
	return bool(TeamMember.objects.filter(user=user, captain=1))