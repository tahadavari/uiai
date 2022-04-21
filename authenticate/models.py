from datetime import datetime, timedelta

from django.conf import settings
from django.db import models

# Create your models here.
from hashids import Hashids

from account.models import User
from core.models import BaseModel
from django.conf import settings
import pytz

class EmailVerifyToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50)


class ForgetPasswordEmailToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50)

    def is_valid(self):
        print(self.created_at , settings.RESET_PASSWORD_TOKEN_LIFE_TIME,datetime.now(tz=pytz.utc))
        return (self.created_at + settings.RESET_PASSWORD_TOKEN_LIFE_TIME) > datetime.now(tz=pytz.utc)

    def delete_user_tokens(self):
        ForgetPasswordEmailToken.objects.filter(user=self.user).delete()
