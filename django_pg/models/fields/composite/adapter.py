from __future__ import absolute_import, unicode_literals
from psycopg2.extensions import adapt, SQL_IN


class CompositeAdapter(object):
    db_type = ''

    def __init__(self, obj):
        self._obj = obj

    def getquoted(self):
        """Return the appropriate SQL for the given object, typecast
        to the registered db_type.
        """
        return '{sql}::{db_type}'.format(
            db_type=self._db_type,
            sql=adapt(tuple(self._obj)).getquoted().decode('utf8'),
        ).encode('utf8')


def adapter_factory(name, db_type):
    return type(name, (CompositeAdapter,), { '_db_type': db_type })
