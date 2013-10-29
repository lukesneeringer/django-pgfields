from __future__ import absolute_import, unicode_literals
from collections import namedtuple
from copy import copy
from django.db import models, connection
from django.db.models.fields.related import RelatedField
from django_pg.models.fields.composite.adapter import adapter_factory
from django_pg.utils import Meta
from django_pg.utils.types import type_exists
from importlib import import_module
from psycopg2.extensions import register_adapter
from psycopg2.extras import CompositeCaster
import re


class CompositeInstance(object):
    def __init__(self, *args, **kwargs):
        # Assign the default values to the instance.
        for key, val in self._defaults.items():
            setattr(self, key, val)

        # If we have positional arguments, convert them to keyword arguments
        # based on our field names.
        for field_name, pos_arg_value in zip(self._field_names, args):
            # Sanity check: Don't allow assignment of a field
            #   as a positional argument *and* a positional argument.
            if field_name in kwargs:
                raise TypeError('%s got multiple values for %s.' % (
                    self.__class__.__name__,
                    field_name,
                ))

            # All is well: Assign the argument into kwargs.
            kwargs[field_name] = pos_arg_value

        # Assign any values that were sent on initialization.
        for key, val in kwargs.items():
            # Sanity Check: Does this field actually exist within
            # this composite type?
            if key not in self._field_names:
                raise KeyError('Unrecognized key: %s' % key)
            setattr(self, key, val)

    def __iter__(self):
        for key in self._field_names:
            yield getattr(self, key)

    def __repr__(self):
        return repr(self.as_namedtuple())

    def as_namedtuple(self):
        return self._namedtuple(*tuple(self))


class CompositeMeta(models.SubfieldBase):
    """Metaclass for CompositeFields."""

    def __new__(cls, name, bases, attrs):
        """Upon creation of the CompositeField subclass, take any fields
        identified in attrs and apply them to sub-fields.
        """
        # Retreive any fields in the "attrs" dictionary and remove them.
        fields = []
        for key, value in copy(attrs).items():
            if isinstance(value, models.Field):
                # Sanity Check: We can't have any kind of related field
                #   within a composite type.
                if isinstance(value, RelatedField):
                    raise TypeError(' '.join((
                        'Composite types cannot contain related fields',
                        'of any kind.',
                    )))

                # Okay, everything is fine.
                fields.append((key, attrs.pop(key)))

        # Sort the fields, such that they are in the order they were
        # instantiated.
        # 
        # This is a trivial task because django.db.models.Field implements
        # __eq__, __lt__, and __gt__ methods that work against the field's
        # creation count.
        fields.sort(key=lambda item: item[1])

        # Create a "_meta" object (mimic how django.db.models.Model does it)
        #   that stores the sub-fields, as well as any other properties
        #   (such as an alternate type name).
        meta_obj = attrs.pop('Meta', Meta())
        if not hasattr(meta_obj, 'db_type') and bases != (models.Field,):
            meta_obj.db_type = re.sub(r'field$', '', name.lower())

        # Store the fields on the meta object.
        if not hasattr(meta_obj, 'fields'):
            meta_obj.fields = []
        meta_obj.fields += fields

        # Instantiate the class
        new_class = models.SubfieldBase.__new__(cls, name, bases, attrs)

        # Add the meta object to the class.
        new_class._meta = meta_obj

        # Sanity check: We actually only want the remaining behavior
        # on *subclasses* of CompositeField, not CompositeField itself.
        if name == 'CompositeField' and bases == (models.Field,):
            return new_class

        # Additionally, create another class that will hold instance values.
        # The `str` on the next two lines is intentional; I want a `str` object
        # regardless of whether this is Python 2 or Python 3.
        class_name = str(re.sub(r'Field$', '', name))
        field_names = [str(i[0]) for i in meta_obj.fields]
        instance_class = type(class_name, (CompositeInstance,), {
            '_defaults': dict(
                [(i[0], i[1].get_default()) for i in meta_obj.fields],
            ),
            '_field_names': field_names,
            '_namedtuple': namedtuple(
                typename=class_name,
                field_names=field_names,
            )
        })

        # Assign the instance class to the field class, so we can
        # get to it from there.
        new_class.instance_class = instance_class

        # Ensure that the type exists in the database.
        # This is the final hook for this; it will ensure the presence
        # of the type if the syncdb or connection creation hooks fail.
        #
        # This is, in particular, needed for testing, since the test
        # database types are copied from the main database, but the tests
        # don't have any guarantee that the main database ever ran.
        new_class.create_type(connection)

        # Create a "caster class" for converting the value that
        #   comes out of the database into our new Python class.
        # For more info, see: http://initd.org/psycopg/docs/extras.html
        caster_class_name = str(class_name + 'Caster')
        new_class.caster = type(caster_class_name, (CompositeCaster,), {
            'make': lambda self, values: instance_class(
                **dict(zip(self.attnames, values))
            ),
        })

        # Register the caster class with psycopg2.
        new_class.register_composite(connection)

        # Register an adapter function with psycopg2. The adapter function
        # tells psycopg2 how to translate our instance class to SQL.
        register_adapter(instance_class, adapter_factory(
            db_type=meta_obj.db_type,
            name=str(class_name + 'Adapter'),
        ))

        # If the instance class has a different name, try to be
        # extra super bonus clever and actually add the instance class
        # to the module.
        if instance_class.__name__ != new_class.__name__:
            module = import_module(new_class.__module__)
            setattr(module, instance_class.__name__, instance_class)

        # If South is installed, then add introspection rules for it.
        try:
            from south.modelsinspector import add_introspection_rules
            add_introspection_rules([
                (
                    (new_class,),
                    [],
                    {
                        'null': ['null', { 'default': True }],
                    },
                )
            ], [r'^{module}\.{class_name}'.format(
                class_name=new_class.__name__,
                module=new_class.__module__.replace('.', r'\.'),
            )])
        except ImportError:
            pass

        # Return the new class.
        return new_class
