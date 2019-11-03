from django.contrib import admin
from .models import BlogType, Blog


# Register your models here.
@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'blog_type', 'get_read_num', 'content', 'create_time', 'last_update_time')

#
# @admin.register(BlogReadNum)
# class BlogReadNum(admin.ModelAdmin):
#     list_display = ('id', 'read_num', 'blog')
