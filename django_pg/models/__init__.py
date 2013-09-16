from __future__ import absolute_import, unicode_literals
from django_pg.utils.gis import gis_backend

if gis_backend:
    from django.contrib.gis.db.models import *
    from django_pg.models.base import Model, Manager, GeoManager
else:
    from django.db.models import *
    from django_pg.models.base import Model, Manager

from django_pg.models.fields import *
