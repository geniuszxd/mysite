from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm


register = template.Library()


@register.simple_tag
def get_comment_form(obj):
    form = CommentForm(initial={'content_type': ContentType.objects.get_for_model(obj),
                                'object_id': obj.pk,
                                'reply_comment_id': 0})
    return form


@register.simple_tag
def get_comment_code(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()


@register.simple_tag
def get_commont_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None).order_by('-time')

