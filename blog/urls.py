from django.urls import path
from . import views


urlpatterns = [
    path("<int:blog_pk>", views.blog_detail, name="blog_detail"),
    path("type/<int:blog_type_pk>", views.blogs_with_type, name="blogs_with_type"),
    path("month/<int:year>/<int:month>", views.blog_with_year_month, name="blogs_with_year_month"),
]
