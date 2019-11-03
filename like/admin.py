from django.contrib import admin
from .models import LikeRecord


# Register your models here.
@admin.register(LikeRecord)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'user')
