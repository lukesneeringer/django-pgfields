from __future__ import absolute_import, unicode_literals
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS


def _detect_gis_backend():
    """Determine whether or not a GIS backend is currently in use,
    to allow for divergent behavior elsewhere.
    """
    # If the connection is from `django.contrib.gis`, then we know that this
    # is a GIS backend.
    if '.gis.' in connections[DEFAULT_DB_ALIAS].__module__:
        return True

    # Annoying case: If we're using a dummy backend (the most likely reason
    # being because, for testing, the database is mocked out), we need to
    # determine GIS presence or absence in such a way that will work on
    # the system.
    #
    # We have to approximate this; essentially, return True if geos is
    # installed, and False otherwise.  We can determine this by trying to
    # import GEOSException.
    if '.dummy.' in connections[DEFAULT_DB_ALIAS].__module__:  # pragma: no cover
        try:
            from django.contrib.gis.geos import GEOSException
            return True
        except ImportError:
            return False

    # Okay, there's no GIS backend in use.
    return False


gis_backend = _detect_gis_backend()
