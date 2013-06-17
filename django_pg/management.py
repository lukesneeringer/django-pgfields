from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django_pg.utils.utf8 import UnicodeAdapter
from psycopg2.extensions import adapters, register_adapter


@receiver(connection_created)
def register_unicode_adapter(sender, connection, **kwargs):
    register_adapter(str, UnicodeAdapter)
