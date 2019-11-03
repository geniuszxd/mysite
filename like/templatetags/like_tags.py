from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeRecord


register = template.Library()


@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    user = context['user']
    if not user.is_authenticated:
        return False
    content_type = ContentType.objects.get_for_model(obj)
    return LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=user).exists()


@register.simple_tag
def get_like_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk).count()
