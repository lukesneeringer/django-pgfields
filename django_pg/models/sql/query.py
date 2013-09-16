from __future__ import absolute_import, unicode_literals
from django.db.models.sql import query
from django_pg.utils.gis import gis_backend

if gis_backend:
    from django.contrib.gis.db.models.sql import query as gis_query
    

DJANGO_PG_QUERY_TERMS = { 'len' }


class Query(query.Query):
    query_terms = query.Query.query_terms.union(DJANGO_PG_QUERY_TERMS)


if gis_backend:
    class GeoQuery(gis_query.GeoQuery):
        query_terms = gis_query.GeoQuery.query_terms.union(
            DJANGO_PG_QUERY_TERMS,
        )
