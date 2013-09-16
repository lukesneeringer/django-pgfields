from __future__ import absolute_import, unicode_literals
from django_pg import models


class Place(models.Model):
    name = models.CharField(max_length=20)
    residents = models.ArrayField(of=models.CharField(max_length=40))
