from django import template

register = template.Library()

@register.filter
def add(value, arg):
    return int(value) + int(arg)

@register.filter
def subtract(value, arg):
    return int(value) - int(arg)

@register.filter
def multiply_by(value, arg):
    return int(value) * int(arg)

@register.filter
def divide(value, arg):
    return int(value) / int(arg)

@register.filter
def divide_by_count(value, arg):
    return int(value) / int(len(arg))

@register.filter
def limit_ceil(value, arg):
    return min(int(value), int(arg))

@register.filter
def limit_floor(value, arg):
    return max(int(value), int(arg))

@register.filter
def get_range(value, end=False):
    if end != False:
        return range(value, end)

    return range(value)

@register.filter
def average_list(value):
    if not len(value):
        return 0

    return sum(value) / float(len(value))
