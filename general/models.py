from django.conf import settings
from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
# Create your models here.

class Team(BaseModel):
    MAIN_TEAM = 1

    TEAM = [
        (MAIN_TEAM,_('MAIN'))
    ]
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    about = models.CharField(max_length=500,null=True,blank=True)
    team = models.IntegerField(choices=TEAM)
    avatar = models.ImageField(upload_to='team/avatar', verbose_name=_('Avatar'))

    def avatar_url(self):
        if self.avatar:
            return settings.CDN_SERVER_PREFIX + self.avatar.url
        else:
            return None

class Setting(BaseModel):
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=50,unique=True)
    value = models.CharField(max_length=1000)

    def __str__(self) -> str:
        return f"{self.name} : {self.key}"


class Message(BaseModel):
    name = models.CharField(max_length=100)
    message = models.CharField(max_length=500)
    email = models.CharField(max_length=100)

class EmailNews(BaseModel):
    email = models.CharField(max_length=100)

class Social(BaseModel):
    name = models.CharField(max_length=100)
    link = models.URLField()
    key = models.CharField(max_length=100,default='social')
    icon = models.CharField(max_length=50,default='lab la-instagram')

    def __str__(self) -> str:
        return self.name