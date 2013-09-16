from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import connections, models
from django.db.models import options
from django.db.utils import DEFAULT_DB_ALIAS
from django_pg.models.query import QuerySet, GeoQuerySet
from django_pg.utils.repr import smart_repr
import importlib
import six


# This is a monkey patch on `django.db.models.options.Options`.
# Adding these two default values allow them as values in Meta inner-classes.
if getattr(settings, 'DJANGOPG_IMPROVED_REPR', False):
    options.DEFAULT_NAMES = (options.DEFAULT_NAMES +
                             ('repr_fields', 'repr_fields_exclude'))


def ManagerFactory(name, superclass, qs=QuerySet):
    """Create a manager class, using the given superclass, and adding
    django_pg's specific behavior.
    """
    # It's completely fine to use our custom manager for related fields,
    # and it's necessary, since we need to ensure that our custom queries
    # and query sets are what are created throughout.
    attrs = {
        'use_for_related_fields': True,
    }

    # The `get_queryset` method changes in Django 1.6; introspect
    # the superclass to see which one we should overwrite.
    import django
    if hasattr(superclass, 'get_queryset'):
        attrs['get_queryset'] = lambda self: qs(self.model, using=self._db)
    else:
        attrs['get_query_set'] = lambda self: qs(self.model, using=self._db)

    # Instantiate and return the Manager.
    #
    # Note: The `str` here is intentional; this should be an instance
    # of the `str` class regardless of whether we are in Python 2 or Python 3.
    # Under Python 2, this would otherwise be a `unicode` object, which
    # won't work under the hood.
    return type(superclass)(str(name), (superclass,), attrs)


Manager = ManagerFactory('Manager', models.Manager)
GeoManager = ManagerFactory('GeoManager', gis_models.GeoManager,
                            qs=GeoQuerySet)


def select_manager():
    """If a manager is defined in the application's Django settings,
    return an instance of it.

    Otherwise, attempt to select the appropriate manager based on
    introspecting the application's database settings, and instantiate
    that one.
    """
    # First, is a manager specified in settings?
    manager_class = getattr(settings, 'DJANGOPG_DEFAULT_MANAGER', None)
    if manager_class:
        # If we got a string, get the actual manager class.
        if isinstance(manager_class, six.text_type):
            # Sanity check: Did I get usable input?
            if '.' not in manager_class:
                raise ImportError(' '.join((
                    'If DJANGOPG_DEFAULT_MANAGER is specified as a string,',
                    'the full dotted module path is required.',
                )))

            # Break out the module and class name.
            manager_module = '.'.join(manager_class.split('.')[:-1])
            manager_class_name = manager_class.split('.')[-1]

            # Import the module.
            module = importlib.import_module(manager_module)

            # Get the class out of the module and return an instance.
            class_ = getattr(module, manager_class_name)
            return class_()
        else:
            return manager_class()

    # There was no manager class specified in settings; attempt
    # to guess one based on database settings.
    connection = connections[DEFAULT_DB_ALIAS]
    if '.gis.' in connection.__module__:
        return GeoManager()
    return Manager()


class Model(models.Model):
    """Base model class for `django_pg`, which extends Django's ORM
    with PostgreSQL-specific extensions.
    """
    objects = select_manager()

    class Meta:
        abstract = True

    def __repr__(self, object_list=None, depth=1):
        """Send down a useful, unambiguous representation of the
        object.
        """
        # Sanity check: Is our improved repr system turned on?
        # If it's not turned on, don't use it: this is an explicit opt-in.
        if not getattr(settings, 'DJANGOPG_IMPROVED_REPR', False):
            return super(Model, self).__repr__()

        # Sanity check: Have we rendered this object already?
        # Avoid a recursion scenario.
        if not object_list:
            object_list = []
        if self in object_list:
            return '**RECURSION**'

        # Get a list of fields to iterate over. By default this is
        # every field, but this new system allows for the model to define
        # which fields should be included in its repr.
        if hasattr(self._meta, 'repr_fields'):
            field_names = self._meta.repr_fields
        else:
            field_names = [i.name for i in self._meta.fields]
            for field_name in getattr(self._meta, 'repr_fields_exclude', []):
                if field_name in field_names:
                    field_names.remove(field_name)

        # What is our indentation level?
        tab = ' ' * depth * 4

        # Define our two built-in templates for our improved repr.
        repr_templates = {
            'single_line': ('<%(class_name)s: {%(members)s}>', ', '),
            'multi_line': (
                '<%(class_name)s: {\n%(tab)s%(members)s\n%(untab)s}>',
                ',\n%(tab)s',
            ),
        }

        # Determine the actual template in use.
        template = getattr(settings, 'DJANGOPG_REPR_TEMPLATE', 'single_line')
        if isinstance(template, six.text_type):
            template = repr_templates[template]

        # Return the improved repr.
        return template[0] % {
            'class_name': self.__class__.__name__,
            'members': (template[1] % { 'tab': tab }).join(
                ['%r: %s' % (k, smart_repr(getattr(self, k),
                                           depth=depth + 1,
                                           object_list=object_list + [self]))
                for k in field_names]
            ),
            'tab': tab,
            'untab': tab[:-4],
        }
