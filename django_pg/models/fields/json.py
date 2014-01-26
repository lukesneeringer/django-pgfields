from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.postgresql_psycopg2.version import get_version
from django_pg.utils.decorators import validate_type
from django_pg.utils.south import south_installed
import json
import re
import six


@six.add_metaclass(models.SubfieldBase)
class JSONField(models.Field):
    """Specialized text field that holds JSON in the database, which is
    represented within Python as (usually) a dictionary.
    """
    def __init__(self, null=True, blank=True, type=None, default=None,
                       *args, **kwargs):
        # Sanity check: If a type is specified, ensure it's a type
        # that has a JSON analogue.
        if type not in (dict, list, six.text_type, int, float, bool, None):
            raise TypeError('If a `type` is specified for JSONField, it must '
                            'be dict, list, %s, int, float, or bool.' %
                            six.text_type.__name__)

        # Save the type to this field instance; we refer back to it
        # when validation is done.
        self._type = type

        # Determine an appropriate default for the given JSON type,
        # using empty dict if no type is specified.
        if self._type and not default:
            default = json.dumps(self._type())

        # Run the superclass constructor.
        super(JSONField, self).__init__(*args, null=null, blank=blank,
                                        default=default, **kwargs)

    def db_type(self, connection):
        return 'json' if get_version(connection) >= 90200 else 'text'

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        """Raise an exception; PostgreSQL 9.2 is unable to do lookups
        of any kind on JSON values.
        """
        # TODO: PostgreSQL 9.3 contains full support for lookups on JSON
        # fields. When PostgreSQL 9.3 is released, circle back and support
        # lookups appropriately.
        raise TypeError(' '.join((
            'Lookups of any kind on JSON fields are not permitted',
            'in PostgreSQL. This will change in PostgreSQL 9.3',
        )))

    def get_prep_value(self, value):
        return json.dumps(value)
        
    @validate_type
    def to_python(self, value):
        """Given input that may be a Python value and may be JSON, return
        the appropriate Python value.
        """
        # Lists, dicts, ints, and booleans are clearly fine as is.
        if not isinstance(value, six.text_type):
            return value
            
        # Properly identify numbers and return them as ints or floats.
        if self._type != six.text_type:
            if re.match(r'^[\d]+$', value):
                return int(value)
            if (re.match(r'^[\d]+\.[\d]*$', value) or
                            re.match(r'^\.[\d]+$', value)):
                return float(value)
            
            # Try to tell the difference between a "normal" string
            # and serialized JSON.
            #
            # Strings that fit these rules are probably serialized JSON.
            if value in ('true', 'false', 'null'):
                return json.loads(value)
            if value.startswith(('{','[',)) and value.endswith(('}',']')):
                return json.loads(value)

        # Properly identify JSON strings and return them as such.
        #
        # Note: This processing should occur even if the type for
        # this field is set to str.
        if value.startswith('"') and value.endswith('"'):
            return json.loads(value)
                        
        # Okay, this is not a JSON string. Return the unadulterated value.
        return value


# If South is installed, then tell South how to properly
# introspect a JSONField.
if south_installed:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (JSONField,),
        [],
        {
            'blank': ['blank', { 'default': True }],
            'default': ['default', { 'default': '{}' }],
            'null': ['null', { 'default': True }],
        },
    )], (r'^django_pg\.models\.fields\.json\.JSONField',))
