from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.aggregates import Sum
from .models import ReadNum, ReadDetail


def read_once(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read' % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
        #     blog_read_num = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        # else:
        #     blog_read_num = ReadNum(content_type=ct, object_id=obj.pk)
        blog_read_num, _created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        blog_read_num.read_num += 1
        blog_read_num.save()

        today = timezone.now().date()
        read_detail, _created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, read_date=today)
        read_detail.read_num += 1
        read_detail.save()
    return key


def get_seven_days_read():
    date_strings = []
    read_nums = []
    today = timezone.now().date()
    for i in range(7, 0, -1):
        date_delta = timedelta(days=i)
        date = today - date_delta
        date_string = date.strftime('%m/%d')
        date_strings.append(date_string)
        read_num_date = ReadDetail.objects.filter(read_date=date).aggregate(total=Sum("read_num"))
        read_nums.append(read_num_date["total"] or 0)
    return date_strings, read_nums


def get_yesterday_hot(content_type):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    read_nums = ReadDetail.objects.filter(content_type=content_type, read_date=yesterday).order_by('-read_num')
    return read_nums[:5]


def get_seven_days_hot(content_type):
    today = timezone.now().date()
    date_flag = today - timedelta(days=7)
    read_nums = ReadDetail.objects.filter(content_type=content_type, read_date__gte=date_flag, read_date__lt=today).order_by('-read_num')
    return read_nums

