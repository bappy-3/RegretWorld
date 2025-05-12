# from django import template

# register = template.Library()


# def range_filter(value):
#     return value[0:500] + "......."


# register.filter('range_filter', range_filter)


from django import template

register = template.Library()

# Define the range_filter function
@register.filter(name='range_filter')
def range_filter(value):
    return value[0:500] + "......."  

# Define the anonymous_name filter
@register.filter(name='anonymous_name')
def anonymous_name(value, user):
    # Check if the user is anonymous
    if user.is_authenticated:
        return value
    else:
        return "Anonymous User"  # Return "Anonymous User" if the user is not authenticated


