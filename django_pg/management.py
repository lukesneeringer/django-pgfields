from __future__ import absolute_import, unicode_literals
from django.db import connections
from django.db.backends.signals import connection_created
from django.db.models.loading import get_models
from django.dispatch import receiver
from django_pg.utils.utf8 import UnicodeAdapter
from psycopg2.extensions import adapters, register_adapter
import django


@receiver(connection_created)
def register_unicode_adapter(sender, connection, **kwargs):
    register_adapter(str, UnicodeAdapter)


# A `pre_syncdb` signal to create the necessary types is desirable,
#   but only supported on Django >= 1.6.
# Prior to Django 1.6, the only mechanism is to use the `connection_created`
#   signal, which will run through all models whenever a new connection is
#   made and do a brute-force check for type presence.
if django.VERSION >= (1, 6):
    from django.db.models.signals import pre_syncdb

    @receiver(pre_syncdb)
    def before_syncdb(sender, app, create_models, db, **kwargs):
        """Check the appropriate database and ensure that any
        fields that the models expect do, in fact, exist.
        """
        for model in create_models:
            connection = connections[db]

            # Iterate over the fields and create any type that does not
            # already exist.
            for field in model._meta.fields:
                if hasattr(field, 'create_type'):
                    field.create_type(connection)

                    # If we were missing a field type, then the composite
                    # caster won't be registered with psycopg2 either.
                    field.register_composite(connection)
else:
    @receiver(connection_created)
    def on_connection_created(sender, connection, **kwargs):
        """When a connection is created, ensure that required custom
        database types are created.
        """
        for model in get_models():
            # Iterate over the fields and create any type that does not
            # already exist.
            for field in model._meta.fields:
                if hasattr(field, 'create_type'):
                    field.create_type(connection)

                    # If we were missing a field type, then the composite
                    # caster won't be registered with psycopg2 either.
                    field.register_composite(connection)
