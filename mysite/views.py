from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Sum
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read, get_yesterday_hot
from blog.models import Blog


def get_seven_days_hot():
    today = timezone.now().date()
    date_flag = today - timedelta(days=7)
    seven_days_hot = Blog.objects.filter(read_detail__read_date__lt=today, read_detail__read_date__gte=date_flag) \
                                 .values('id', 'title') \
                                 .annotate(read_num_sum=Sum('read_detail__read_num')) \
                                 .order_by('-read_num_sum')
    return seven_days_hot[:5]


def home(request):
    context = dict()
    seven_days_dates, seven_days_read_nums = get_seven_days_read()
    context["seven_days_dates"] = seven_days_dates
    context["seven_days_read_nums"] = seven_days_read_nums
    context['yesterday_hot'] = get_yesterday_hot(ContentType.objects.get_for_model(Blog))
    seven_days_hot = cache.get('seven_days_hot')
    if seven_days_hot is None:
        seven_days_hot = get_seven_days_hot()
        cache.set('seven_days_hot', seven_days_hot, 3600)
    context['seven_days_hot'] = seven_days_hot
    return render(request, "home.html", context)
