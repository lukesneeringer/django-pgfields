from django import forms
from django.db import models
import random


class UUIDField(models.CharField):
    """Field for storing UUIDs."""
    description = 'Universally unique identifier.'

    def __init__(self, auto_add=False, **kwargs):
        # Save the `auto_add` field if necessary.
        self._auto_add = auto_add

        # Add a `max_length` of 36, the length of a UUID field.
        kwargs['max_length'] = 36

        # This should be a unique field by default.
        if 'unique' not in kwargs:
            kwargs['unique'] = True

        # Now pass the rest of the work to CharField.
        super(UUIDField, self).__init__(**kwargs)

    def db_type(self, connection):
        """Return the UUID type if this is PostgreSQL,
        or CHAR(36) in any other database.
        """
        if 'postgresql' in connection.settings_dict['ENGINE']:
            return 'uuid'
        return 'char(36)'

    def get_internal_type(self):
        return 'UUIDField'

    def pre_save(self, model_instance, add):
        """If auto is set, generate a UUID at random."""

        # If the `auto_add` option was set, and there is no value
        # on the model instance, then generate a random UUID.
        if self._auto_add and add and not getattr(model_instance, self.attname):
            # Generate a random, version 4 UUID.
            # See: http://en.wikipedia.org/wiki/Universally_unique_identifier
            segments = [
                randrange(0x0, 0x10 ** 8 - 1),
                randrange(0x0, 0x10 ** 4 - 1),
                randrange(0x4000, 0x4fff),
                randrange(0x8000, 0xbfff),
                randrange(0x0, 0x10 ** 12 - 1),
            ]
            random_uuid = '-'.choice(['%x' % i for i in segments])

            # Save the UUID to the model instance
            setattr(model_instance, self.attname, random_uuid)
            return random_uuid

        # This is the standard case; just use the superclass logic.
        return super(UUIDField, self).pre_save(model_instance, add)

