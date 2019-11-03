import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, '', settings.EMAIL_HOST_USER, [self.email], fail_silently=self.fail_silently, html_message=self.text)


# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    root = models.ForeignKey("self", null=True, related_name='sub_comments', on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, related_name='child_comments', on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, null=True, related_name='replies', on_delete=models.CASCADE)

    def send_mail(self):
        # 发送邮件
        if self.parent is None:
            subject = "有人评论你的博客"
            email = self.content_object.get_email()
        else:
            subject = "有人回复你的评论"
            email = self.reply_to.email
        if email != "":
            context = {"comment_content": self.text, 'url': self.content_object.get_url()}
            text = render_to_string("comment/send_mail.html", context)
            send_mail_thread = SendMail(subject, text, email)
            send_mail_thread.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['time']
