from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=20, verbose_name='昵称')

    def __str__(self):
        return "<Profile: %s for %s>" % (self.alias, self.user.username)


def get_alias(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.alias
    else:
        return ""


def alias_is_empty(self):
    return not Profile.objects.filter(user=self).exists()


def alias_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.alias
    else:
        return self.username


User.alias = get_alias
User.alias_is_empty = alias_is_empty
User.alias_or_username = alias_or_username
