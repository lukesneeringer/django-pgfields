from importlib import import_module
import os
import sys


# Get the project root directory, and add it to `sys.path`.
current_file = __file__
if __name__ == '__main__':
    current_file = '%s/%s' % (os.getcwd(), __file__)
sys.path.insert(0, os.path.realpath(os.path.dirname(current_file) + '/../'))

# Add the Django settings module to the environment.
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

# Run tests.
from django.core.management import call_command

if __name__ == '__main__':
    args = sys.argv[1:]

    from django.conf import settings
    from django.db.backends.signals import connection_created
    from django.db.models.loading import get_apps, get_models
    from django.dispatch import receiver
    from django.utils.module_loading import module_has_submodule
    from django_pg import models
    from django_pg.utils.types import type_exists
    from psycopg2.extras import register_composite

    @receiver(connection_created)
    def on_connection_created(sender, connection, **kwargs):
        """When a connection is created, ensure that required custom
        database types are created, as our standard processing only handles
        this on the "real" database (not the test one).
        """
        for model in get_models():
            # Iterate over the fields and create any type that does not
            # already exist.
            for field in model._meta.fields:
                if hasattr(field, 'create_type'):
                    field.create_type(connection)

                    # If we were missing a field type, then the composite
                    # caster won't be registered with psycopg2 either.
                    field.register_composite(connection.cursor())

    call_command('test', *args)
