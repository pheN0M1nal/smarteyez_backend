from django.db import models
import secrets
# from django.apps import apps
import gc
from django.utils import timezone


def queryset_iterator(queryset, chunksize=100):
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


class BaseModelMixin(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    def get_identifier(self):
        return secrets.token_hex(5) + str(int(timezone.now().timestamp()))
    def is_instance_exist(self):
        return self.__class__.objects.filter(id=self.id).exists()

    @property
    def current_instance(self):
        return self.__class__.objects.get(id=self.id)

    @classmethod
    def efficient_queryset_iterator(cls):
        return queryset_iterator(cls.objects)

    def create_token(self):
        # Create random 16 bytes hex token
        return secrets.token_hex(16)

    def __str__(self):
        return self.__class__.__name__

    class Meta:
        abstract = True


def create_token():
    # Create random 16 bytes hex token
    return secrets.token_hex(16)
