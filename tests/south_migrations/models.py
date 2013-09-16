from __future__ import absolute_import, unicode_literals
from django_pg import models
from tests.composite.fields import BookField


class Author(models.Model):
    name = models.CharField(max_length=75)
    uuid = models.UUIDField(null=True)
    books = models.ArrayField(of=BookField)
    data = models.JSONField(default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
