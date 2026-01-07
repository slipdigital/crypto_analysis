from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable key."""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_gain(ticker_dict, days):
    """Get gain value for a specific number of days."""
    if ticker_dict is None:
        return None
    key = f'gain_{days}d'
    return ticker_dict.get(key)

@register.filter
def startswith(value, arg):
    """Check if a string starts with a given substring."""
    if value is None:
        return False
    return str(value).startswith(arg)
