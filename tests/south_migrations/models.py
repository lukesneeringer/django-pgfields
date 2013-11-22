from __future__ import absolute_import, unicode_literals
from django.test.utils import override_settings
from django_pg import models
from tests.composite.fields import BookField


with override_settings(DJANGOPG_DEFAULT_UUID_PK=True):
    class Author(models.Model):
        name = models.CharField(max_length=75)
        uuid = models.UUIDField(null=True)
        books = models.ArrayField(of=BookField)
        data = models.JSONField(default=None)
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)
