from .models import LikeRecord
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType


def success_response(like_count):
    return JsonResponse({'status': 'SUCCESS',
                         'like_count': like_count})


def error_response(message):
    return JsonResponse({'status': 'ERROR',
                         'message': message})


def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return error_response('用户未登录')

    content_type = ContentType.objects.get(model=request.GET.get('content_type'))
    object_id = request.GET.get('object_id')

    cancel = request.GET.get('cancel') == 'true'
    exists = LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists()
    if exists:
        if not cancel:
            message = '不能重复点赞'
            return error_response(message)
        LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user).delete()
    else:
        if cancel:
            message = '未点赞，不可取消'
            return error_response(message)
        LikeRecord(content_type=content_type, object_id=object_id, user=user).save()
    like_count = LikeRecord.objects.filter(content_type=content_type, object_id=object_id).count()
    return success_response(like_count)