from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator
from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
from .models import BlogType, Blog
from read_statistics.utils import read_once
from user.forms import LoginForm
# from comment.models import Comment
# from comment.forms import CommentForm
# from django.contrib.contenttypes.models import ContentType
# from read_statistics.models import ReadNum


# Create your views here.
def blog_list(request):
    blogs_all = Blog.objects.all()
    context = get_page_numbers(request, blogs_all)
    return render(request, "blog/blog_list.html", context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    cookie_key = read_once(request, blog)

    # if not request.COOKIES.get('blog_%s_read' % blog_pk):
    #     ct = ContentType.objects.get_for_model(Blog)
    #     if ReadNum.objects.filter(content_type=ct, object_id=blog_pk).count():
    #         blog_read_num = ReadNum.objects.get(content_type=ct, object_id=blog_pk)
    #     else:
    #         blog_read_num = ReadNum(content_type=ct, object_id=blog_pk)
    #     blog_read_num.read_num += 1
    #     blog_read_num.save()

    # if not request.COOKIES.get('blog_%s_read' % blog_pk):
    #     if BlogReadNum.objects.filter(blog=blog).count():
    #         blog_read_num = BlogReadNum.objects.get(blog=blog)
    #     else:
    #         blog_read_num = BlogReadNum(blog=blog)
    #     blog_read_num.read_num += 1
    #     blog_read_num.save()

    context = {"blog": blog}
    context["previous_blog"] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context["next_blog"] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context["login_form"] = LoginForm()

    # content_type = ContentType.objects.get_for_model(blog)
    # context["comments"] = Comment.objects.filter(content_type=content_type, object_id=blog.pk, parent=None).order_by('-time')
    # context["comment_count"] = Comment.objects.filter(content_type=content_type, object_id=blog.pk).count()
    # context['comment_form'] = CommentForm(initial={'content_type': content_type, 'object_id': blog.pk, 'reply_comment_id': 0})

    response = render(request, "blog/blog_detail.html", context)
    response.set_cookie(cookie_key, 'true', max_age=3600)
    return response


def blog_with_year_month(request, year, month):
    blogs_all = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_page_numbers(request, blogs_all)
    context["blog_year_month"] = "%s年%sSSS月" % (year, month)
    return render(request, "blog/blog_with_type.html", context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all = Blog.objects.filter(blog_type=blog_type)
    context = get_page_numbers(request, blogs_all)
    context["type"] = blog_type.type_name
    return render(request, "blog/blog_with_type.html", context)


def get_page_numbers(request, blogs_all):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(blogs_all, settings.PAGE_NUMBER)
    page = paginator.get_page(page_num)
    page_numbers = [x for x in range(page.number-2, page.number+3) if x in page.paginator.page_range]
    if page_numbers[0] > 2:
        page_numbers.insert(0, "...")
    if page_numbers[-1] < page.paginator.num_pages - 1:
        page_numbers.append("...")
    if page_numbers[0] != 1:
        page_numbers.insert(0, 1)
    if page_numbers[-1] != page.paginator.num_pages:
        page_numbers.append(page.paginator.num_pages)
    context = dict()
    context["page"] = page
    context["page_numbers"] = page_numbers

    years_months = Blog.objects.dates("create_time", "month", order="DESC")
    years_months_dict = {}
    for year_month in years_months:
        blog_count = Blog.objects.filter(create_time__year=year_month.year,
                                         create_time__month=year_month.month).count()
        years_months_dict[year_month] = blog_count
    context["blog_times"] = years_months_dict

    # blog_types = BlogType.objects.all()
    # for blog_type in blog_types:
    #     blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
    # context["blog_types"] = blog_types

    context["blog_types"] = BlogType.objects.annotate(blog_count=Count('blog')) # annotate方法，延迟统计
    return context
