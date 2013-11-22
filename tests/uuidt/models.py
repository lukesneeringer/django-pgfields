from __future__ import absolute_import, unicode_literals
from django.test.utils import override_settings
from django_pg import models


with override_settings(DJANGOPG_DEFAULT_UUID_PK=True):
    class Movie(models.Model):
        id = models.UUIDField(auto_add=True, primary_key=True)
        title = models.CharField(max_length=50)

    class SomethingElse(models.Model):
        title = models.CharField(max_length=50)


class Game(models.Model):
    title = models.CharField(max_length=50)
    uuid = models.UUIDField()


class Book(models.Model):
    title = models.CharField(max_length=50)
    uuid = models.UUIDField(null=True)
