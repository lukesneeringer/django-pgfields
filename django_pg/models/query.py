from __future__ import absolute_import, unicode_literals
from django.db.models import query
from django_pg.utils.gis import gis_backend

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
    def __init__(self, model=None, query=None, using=None):
        # Preserve all of the functionality of QuerySet, but
        # use our Query subclass instead of the Django stock one.
        query = query or Query(model, where=WhereNode)
        super(QuerySet, self).__init__(model=model, query=query, using=using)


if gis_backend:
    class GeoQuerySet(gis_query.GeoQuerySet):
        """GeoQuerySet subclass that adds support for PostgreSQL
        specific extensions provided by django_pg.
        """
        def __init__(self, model=None, query=None, using=None):
            # Preserve all of the functionality of QuerySet, but
            # use our Query subclass instead of the Django stock one.
            query = query or GeoQuery(model, where=GeoWhereNode)
            super(GeoQuerySet, self).__init__(model=model, query=query,
                                              using=using)
