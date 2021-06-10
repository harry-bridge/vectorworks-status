from django import template

register = template.Library()


@register.filter
def to_space(value, arg):
    return value.replace(arg, " ")
