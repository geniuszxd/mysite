from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_form_enabled(context, user_enabled, visitor_enabled):
    user = context['user']
    if (user.is_authenticated and user_enabled) or ((not user.is_authenticated) and visitor_enabled):
        return True
    else:
        return False
