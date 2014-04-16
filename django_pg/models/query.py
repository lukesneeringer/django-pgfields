from __future__ import absolute_import, unicode_literals
from django.db.models import query
from django_pg.utils.gis import gis_backend
import six

if gis_backend:
    from django.contrib.gis.db.models import query as gis_query
    from django_pg.models.sql.query import Query, GeoQuery
    from django_pg.models.sql.where import WhereNode, GeoWhereNode
else:
    from django_pg.models.sql.query import Query
    from django_pg.models.sql.where import WhereNode


class QuerySet(query.QuerySet):
    """QuerySet subclass that adds support for PostgreSQL
    specific extensions provided by django_pg.
    """
    def __init__(self, model=None, query=None, using=None, hints=None):
        # Attach the `hints` argument if and only if the `query.QuerySet`
        # constructor will accept it (Django >= 1.7).
        constructor = super(QuerySet, self).__init__
        kwargs = {}
        if 'hints' in constructor.__code__.co_varnames:
            kwargs['hints'] = hints

        # Preserve all of the functionality of QuerySet, but
        # use our Query subclass instead of the Django stock one.
        query = query or Query(model, where=WhereNode)
        super(QuerySet, self).__init__(model=model, query=query, using=using,
                                       **kwargs)


if gis_backend:
    class GeoQuerySet(gis_query.GeoQuerySet):
        """GeoQuerySet subclass that adds support for PostgreSQL
        specific extensions provided by django_pg.
        """
        def __init__(self, model=None, query=None, using=None, hints=None):
            # Attach the `hints` argument if and only if the
            # `gis_query.GeoQuerySet` constructor will accept it
            # (Django >= 1.7).
            constructor = super(GeoQuerySet, self).__init__
            kwargs = {}
            if 'hints' in constructor.__code__.co_varnames:
                kwargs['hints'] = hints

            # Preserve all of the functionality of QuerySet, but
            # use our Query subclass instead of the Django stock one.
            query = query or GeoQuery(model, where=GeoWhereNode)
            super(GeoQuerySet, self).__init__(model=model, query=query,
                                              using=using, **kwargs)
