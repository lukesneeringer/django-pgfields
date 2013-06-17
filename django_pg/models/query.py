from django.db.models import query
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