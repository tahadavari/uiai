from django.conf import settings
from django.db import models
from hashids import Hashids
from django.utils.translation import gettext_lazy as _

from core.manager import BaseManager

hashids = Hashids(salt=settings.HASH_SALT, min_length=10)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    hash = models.CharField(max_length=20, verbose_name=_('Hash'))

    objects = BaseManager()
    def save(self, *args, **kwargs):
        super(BaseModel, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = hashids.encode(self.id)
            self.save(update_fields=['hash'])
