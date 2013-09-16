from __future__ import absolute_import, unicode_literals
from django_pg import models
from django_pg.utils.gis import gis_backend


if gis_backend:
    class Place(models.Model):
        name = models.CharField(max_length=50)
        books = models.ArrayField(of=models.CharField(max_length=100))
        bounds = models.PolygonField()
