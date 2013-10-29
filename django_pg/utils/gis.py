from __future__ import absolute_import, unicode_literals
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS


gis_backend = any((
    '.gis.' in connections[DEFAULT_DB_ALIAS].__module__,
    '.dummy.' in connections[DEFAULT_DB_ALIAS].__module__,
))
