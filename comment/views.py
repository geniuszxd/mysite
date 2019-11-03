# from django.shortcuts import redirect, render
# from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm


# Create your views here.
def submit_comment(request):
    user = request.user

    '''
    # 检查数据
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if not user.is_authenticated:
        return render(request, "error.html", {'message': '用户未登录。', 'backward': referer})
    comment_content = request.POST.get('comment_content', '').strip()
    if comment_content == '':
        return render(request, "error.html", {'message': '评论内容不可为空。', 'backward': referer})
    try:
        content_type = request.POST.get('content_type', '')  # 这里是从前端传回的字符串
        object_id = int(request.POST.get('object_id', ''))
        model_class = ContentType.objects.get(model=content_type).model_class()  # 反射
        model_object = model_class.objects.get(pk=object_id)
    except Exception:
        return render(request, "error.html", {'message': '评论对象不存在。', 'backward': referer})

    # 检查通过，提交评论
    comment = Comment()
    comment.content_object = model_object
    comment.user = user
    comment.text = comment_content
    comment.save()
    '''

    comment_form = CommentForm(request.POST, user=user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = user
        comment.content_object = comment_form.cleaned_data['content_object']
        comment.text = comment_form.cleaned_data['comment_content']
        parent = comment_form.cleaned_data['parent']
        if parent is not None:
            comment.parent = parent
            comment.root = parent.root if parent.root is not None else parent
            comment.reply_to = parent.user
        comment.save()

        # 发送邮件
        comment.send_mail()

        data = {'status': "SUCCESS",
                'id': comment.id,
                'time': comment.time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': user.alias_or_username(),
                'text': comment.text,
                'reply_to': comment.reply_to.alias_or_username() if comment.reply_to is not None else '',
                'root': comment.root.pk if comment.root is not None else ''}

    else:
        data = {'status': "ERROR", 'message': list(comment_form.errors.values())[0][0]}
    return JsonResponse(data)

