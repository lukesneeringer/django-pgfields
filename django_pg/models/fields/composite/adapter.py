from __future__ import absolute_import, unicode_literals
from django.db import connection
from psycopg2 import extensions
from psycopg2.extensions import adapt, SQL_IN


class CompositeAdapter(object):
    db_type = ''

    def __init__(self, obj):
        self._obj = obj

    def getquoted(self):
        """Return the appropriate SQL for the given object, typecast
        to the registered db_type.
        """
        # Prepare an adapted object from the tuple form of this
        # composite instance.
        adapted = adapt(tuple(self._obj))
        adapted.prepare(connection.connection)

        # Return the appropriate SQL fragment.
        return '{sql}::{db_type}'.format(
            db_type=self._db_type,
            sql=adapted.getquoted().decode('utf8'),
        ).encode('utf8')


def adapter_factory(name, db_type):
    return type(name, (CompositeAdapter,), { '_db_type': db_type })
