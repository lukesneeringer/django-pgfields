from __future__ import absolute_import, unicode_literals
from copy import copy
from django.core.management.color import no_style
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.db.models.options import Options
from django_pg.models.fields.composite.meta import CompositeMeta
from django_pg.utils.types import type_exists
from psycopg2.extras import register_composite
import six


@six.add_metaclass(CompositeMeta)
class CompositeField(models.Field):
    """Field class for storing PostgreSQL composite types."""

    def __init__(self, *args, **kwargs):
        # With composite fields, we need "null" and "blank"
        # to consistently be set to True.
        kwargs['null'] = True
        super(CompositeField, self).__init__(*args, **kwargs)

    @property
    def field_names(self):
        """Return the ordered list of fields."""
        return [field_name for field_name, field in self._meta.fields]

    @classmethod
    def create_type(cls, connection):
        """Create the appropriate type in the database, if and only if
        it does not already exist.
        """
        # Sanity check: Are we using a dummy database?
        # An application using django-pgfields may disable their database
        # **entirely** for testing purposes. If this happens, this should
        # be a no-op, rather than an error.
        if connection.vendor in ('dummy', 'unknown'):
            return

        # Retreive the SQL to create the type.
        sql = cls.create_type_sql(connection, only_if_not_exists=True)
        cursor = connection.cursor()

        # Actually execute the SQL, thereby creating the composite
        # type in the database.
        for sql_stmt in sql.split(';'):
            if not sql_stmt.strip():
                continue
            cursor.execute(sql_stmt)

    @classmethod
    def create_type_sql(cls, connection, style=no_style(),
                                         only_if_not_exists=False ):
        """Return the appropriate SQL to create the custom type in the
        database.
        """
        answer = []

        # Get the name of the database type.
        db_type_name = cls.db_type(connection)
        qn = connection.ops.quote_name

        # Iterate over the sub-fields and construct the SQL for
        # construction of each of them.
        if not only_if_not_exists or not type_exists(connection, db_type_name):
            subfield_type_defs = []
            for key, field in cls._meta.fields:
                subfield_type_defs.append(
                    '    %s %s' % (
                        style.SQL_FIELD(qn(key)),
                        style.SQL_COLTYPE(field.db_type(connection)),
                    )
                )

            # Return the final SQL to create the type.
            sql = []
            sql.append(style.SQL_KEYWORD('CREATE TYPE '))
            sql.append(style.SQL_TABLE(qn(db_type_name)))
            sql.append(style.SQL_KEYWORD(' AS'))
            sql.append(' (\n')
            sql.append(',\n'.join(subfield_type_defs))
            sql.append('\n)')
            answer.append(''.join(sql) + '\n;')

        # Iterate over sub-fields and add any pre-create SQL that
        #   they may require.
        # It's worth noting that if the sub-fields do need pre-create SQL,
        #   it would need to be executed first.
        # Therefore, *prepend* the sub-field SQL if it exists.
        for field_name, field in cls._meta.fields:
            if hasattr(field, 'create_type_sql'):
                answer.insert(0, field.create_type_sql(connection, style,
                                    only_if_not_exists=only_if_not_exists))

        # Return the answer.
        return ';\n'.join(answer)

    @classmethod
    def db_type(cls, connection=None):
        """Return the appropriate PostgreSQL type, which
        is the type name with which this CompositeField was declared.
        """
        # Return the type name with which this field was declared;
        # we must simply assert that it is a PG composite type.
        return cls._meta.db_type

    @classmethod
    def get_fields(cls):
        return copy(cls._meta.fields)

    @classmethod
    def get_field_by_name(cls, field_name):
        return { k: v for k, v in cls._meta.fields }[field_name]

    @classmethod
    def register_composite(cls, connection, globally=True):
        """Register this composite type with psycopg2."""

        # Sanity check: Are we using a dummy database?
        # An application using django-pgfields may disable their database
        # **entirely** for testing purposes. If this happens, this should
        # be a no-op, rather than an error.
        if connection.vendor in ('dummy', 'unknown'):
            return

        # Register the composite type with psycopg2.
        return register_composite(str(cls.db_type()), connection.cursor(),
            factory=cls.caster,
            globally=globally,
        )

    @classmethod
    def type_exists(cls, connection):
        return type_exists(connection, cls._meta.db_type)

    def get_prep_lookup(self, lookup_type, value):
        """Return the appropriate value for a database lookup."""
        # We only understand the `exact` lookup type at this time.
        if lookup_type == 'exact':
            return self.to_python(value)
        raise TypeError('Invalid lookup type: %s' % lookup_type)

    def to_python(self, value):
        """Convert the value to the appropriate Python type prior
        to assigning it.
        """
        # If the value is the instance class, then pass it through
        # unaltered.
        if isinstance(value, self.instance_class):
            for name, field in self.get_fields():
                setattr(value, name, field.to_python(getattr(value, name)))
            return value

        # If the value is None or some other "falsy" value, simply
        # set an empty object of the appropriate class.
        if not value:
            return self.instance_class()

        # If the value is a list or a tuple, convert to the instance
        # class based on values.
        if isinstance(value, (list, tuple)):
            return self.instance_class(
                *[f[1].to_python(v) for f, v in zip(self.get_fields(), value)]
            )

        # The other thing we can understand is a dictionary, or something
        # which can be sent to the dict constructor; pass it as keyword
        # arguments.
        kwargs = {}
        for k, v in dict(value).items():
            f = self.get_field_by_name(k)
            kwargs[k] = f.to_python(v)
        return self.instance_class(**kwargs)
