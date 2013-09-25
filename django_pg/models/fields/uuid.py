from __future__ import absolute_import, unicode_literals
from django.db.models import Field, SubfieldBase
from django_pg.utils.south import south_installed
from psycopg2.extensions import register_adapter
import six
import uuid


@six.add_metaclass(SubfieldBase)
class UUIDField(Field):
    """Field for storing UUIDs."""
    description = 'Universally unique identifier.'

    def __init__(self, auto_add=False, coerce_to=uuid.UUID, **kwargs):
        # Save the `auto_add` and `coerce_to` rules.
        self._auto_add = auto_add
        self._coerce_to = coerce_to

        # This should be a unique field by default.
        if 'unique' not in kwargs:
            kwargs['unique'] = True

        # If `auto_add` is enabled, it should imply that the field
        # is not editable, and should not show up in ModelForms.
        if auto_add and 'editable' not in kwargs:
            kwargs['editable'] = False

        # Blank values shall be nulls.
        if kwargs.get('blank', False) and not kwargs.get('null', False):
            raise AttributeError(' '.join((
                'Blank UUIDs are stored as NULL. Therefore, setting',
                '`blank` to True requires `null` to be True.',
            )))

        # Now pass the rest of the work to CharField.
        super(UUIDField, self).__init__(**kwargs)

    def db_type(self, connection):
        return 'uuid'

    def get_prep_value(self, value):
        """Return a wrapped, valid UUID value."""

        # If the value is None, return None.
        if not value:
            if self.null or self._auto_add:
                return None
            raise ValueError(' '.join((
                'Explicit UUID required unless either `null`',
                'or `auto_add` are True.',
            )))

        # If we already have a UUID, pass it through.
        if isinstance(value, uuid.UUID):
            return value

        # Convert our value to a UUID.
        return uuid.UUID(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Return a UUID object. Also, ensure that psycopg2 is
        aware how to address that object.
        """
        # Register the UUID type with psycopg2.
        register_adapter(uuid.UUID, UUIDAdapter)

        # Run the normal functionality.
        return super(UUIDField, self).get_db_prep_value(value, connection,
                                                        prepared=prepared)

    def pre_save(self, instance, add):
        """If auto is set, generate a UUID at random."""

        # If the `auto_add` option was set, and there is no value
        # on the model instance, then generate a random UUID.
        if self._auto_add and add and not getattr(instance, self.attname):
            random_uuid = uuid.uuid4()

            # Save the UUID to the model instance
            setattr(instance, self.attname, random_uuid)
            return random_uuid

        # This is the standard case; just use the superclass logic.
        return super(UUIDField, self).pre_save(instance, add)

    def to_python(self, value):
        """Return a UUID object."""
        if isinstance(value, self._coerce_to) or not value:
            return value
        return self._coerce_to(value)


class UUIDAdapter(object):
    def __init__(self, value):
        if not isinstance(value, uuid.UUID):
            raise TypeError('UUIDAdapter only understands UUID objects.')
        self.value = value

    def getquoted(self):
        return ("'%s'" % self.value).encode('utf8')

# If South is installed, then tell South how to properly
# introspect a UUIDField.
if south_installed:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (UUIDField,),
        [],
        {
            'auto_add': ['_auto_add', { 'default': False }],
            'coerce_to': ['_coerce_to', { 'default': uuid.UUID }],
            'unique': ['unique', { 'default': True }],
        },
    )], (r'^django_pg\.models\.fields\.uuid\.UUIDField',))
