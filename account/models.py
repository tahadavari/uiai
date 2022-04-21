
from http.client import ACCEPTED
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from hashids import Hashids

from account.manager import MyUserManager
# from authenticate.models import EmailToken
from core.models import BaseModel
from django.contrib.auth.models import PermissionsMixin


# hashids = Hashids(salt=settings.HASH_SALT_EMAIL, min_length=10)


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    LEVEL_MANAGER = 1
    LEVEL_ADMIN = 2
    LEVEL_WRITER = 3
    LEVEL_COMMON = 4

    USER_LEVEL = [
        (LEVEL_MANAGER, _('MANAGER')),
        (LEVEL_ADMIN, _('ADMIN')),
        (LEVEL_WRITER, _('WRITER')),
        (LEVEL_COMMON, _('COMMON')),
    ]
    first_name = models.CharField(max_length=50, verbose_name=_('First name'))
    last_name = models.CharField(max_length=50, verbose_name=_('Last name'))
    username = models.CharField(unique=True, max_length=110, verbose_name=_('Username'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    phone_number = models.CharField(max_length=11, verbose_name=_('Phone number'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Is superuser'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is staff'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    level = models.IntegerField(default=LEVEL_COMMON, choices=USER_LEVEL, verbose_name=_('Level'))
    avatar = models.ImageField(upload_to='user/avatar', verbose_name=_('Avatar'))
    banner = models.ImageField(upload_to='user/banner', verbose_name=_('Avatar'),null=True)
    verify_phone_number = models.BooleanField(default=False, verbose_name=_('Verify phone number'))
    verify_email = models.BooleanField(default=False, verbose_name=_('Verify email'))
    bio = models.CharField(max_length=300, verbose_name=_('bio'), null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects = MyUserManager()

    def get_avatar_path(self):
        return self.avatar.path

    def name(self):
        return self.first_name + self.last_name

    def slug(self):
        return '@' + self.username

    def avatar_url(self):
        if self.avatar:
            return settings.CDN_SERVER_PREFIX + self.avatar.url
        else:
            return None

    def banner_url(self):
        if self.banner:
            return settings.CDN_SERVER_PREFIX + self.banner.url
        else:
            return None

    def send_otp_verify_phone_number(self, phone_number):
        # send sms code
        return True

    def href(self):
        return f"/author/{self.slug()}"

class WriterRequest(BaseModel):
    ACCEPTED_TRUE = 1
    ACCEPTED_FALSE = 0
    ACCEPT = [
        (ACCEPTED_TRUE, _('TRUE')),
        (ACCEPTED_FALSE, _('FLASE'))
    ]
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('User'), related_name='writer_requests')

    accept = models.IntegerField(default=ACCEPTED_FALSE, choices=ACCEPT, verbose_name=_('accept'))
