from django.db.models.sql import query
from django.db.models.sql.constants import QUERY_TERMS


class Query(query.Query):
    """Query subclass which adds support for PostgreSQL specific
    extensions provided by `django_pg`.
    """

    # Add additional query terms which some fields understand.
    query_terms = QUERY_TERMS.union(set([
        'len',
    ]))