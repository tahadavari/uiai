from django.db import models
from django.http import Http404


class BaseManager(models.Manager):
    def hash(self, hash):
        query_set = self.filter(hash=hash).first()
        if query_set:
            return query_set
        else:
            raise Http404

    def hash_or_null(self, hash):
        query_set = self.filter(hash=hash).first()
        if query_set:
            return query_set
        else:
            return None
