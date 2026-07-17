from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def mod(value, arg):
    try:
        return int(value) % int(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
