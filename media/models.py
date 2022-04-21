from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from account.models import User
from core.models import BaseModel


class PostImage(BaseModel):
    url = models.FilePathField(verbose_name=_('Path'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('User'), related_name='users')
    # mediaable_id = models.IntegerField(verbose_name=_('Mediaabel ID'))
    image = models.ImageField(upload_to='post/image/%Y/%m',verbose_name=_('Image'))

    def save(self, *args, **kwargs):
        self.url = settings.CDN_SERVER_PREFIX + self.image.url
        super(PostImage, self).save()
