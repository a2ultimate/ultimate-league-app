from django import template

register = template.Library()


@register.filter()
def groups_sort(groups):

    groups.sort(key=lambda group: len(group['list']))
    return groups