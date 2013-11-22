from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.db import connections, models
from django.db.models import options
from django.db.utils import DEFAULT_DB_ALIAS
from django_pg.utils.gis import gis_backend
from django_pg.utils.repr import smart_repr
import importlib
import six

if gis_backend:
    from django.contrib.gis.db import models as gis_models
    from django_pg.models.query import QuerySet, GeoQuerySet
else:
    from django_pg.models.query import QuerySet


# This is a monkey patch on `django.db.models.options.Options`.
# Adding these two default values allow them as values in Meta inner-classes.
if getattr(settings, 'DJANGOPG_IMPROVED_REPR', False):
    options.DEFAULT_NAMES = (options.DEFAULT_NAMES +
                             ('repr_fields', 'repr_fields_exclude'))

# Add support for `select_related` and `prefetch_related` as a Meta option.
# This adds a substantial level of convenience; otherwise, the developer
# is often forced to make a Manager to get this database efficiency.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('prefetch_related',
                                                 'select_related')


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
    def _get_qs(self):
        queryset = qs(self.model, using=self._db)

        # If the model's `Meta` specifies a `select_related` or
        # `prefetch_related` value, the queryset should automatically
        # apply that.
        for rel_type in ('select_related', 'prefetch_related'):
            rel = getattr(self.model._meta, rel_type, ())
            if isinstance(rel, (six.text_type, six.binary_type)):
                rel = (rel,)
            if rel:
                queryset = getattr(queryset, rel_type)(*rel)

        # Return the queryset.
        return queryset

    if hasattr(superclass, 'get_queryset'):
        attrs['get_queryset'] = _get_qs
    else:
        attrs['get_query_set'] = _get_qs

    # Instantiate and return the Manager.
    #
    # Note: The `str` here is intentional; this should be an instance
    # of the `str` class regardless of whether we are in Python 2 or Python 3.
    # Under Python 2, this would otherwise be a `unicode` object, which
    # won't work under the hood.
    return type(superclass)(str(name), (superclass,), attrs)


Manager = ManagerFactory('Manager', models.Manager)
if gis_backend:
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


class ModelBase(models.base.ModelBase):
    """Subclass of the ModelBase metaclass which understands how to
    add a UUID primary key instead of an integer primary key if asked.
    """
    def _prepare(cls):
        opts = cls._meta

        # If (and only if) we've been asked to through the
        # `DJANGOPG_DEFAULT_UUID_PK` setting, create a primary key that is a
        # UUID rather than an integer.
        if getattr(settings, 'DJANGOPG_DEFAULT_UUID_PK', False):
            if opts.pk is None:
                # Django has a system where it checks for appropriate
                # fields on parent models, if there are any.
                #
                # There's no good way to hook that in other than by copying
                # that piece of the function, so I do so here.
                #
                # Code is taken from django/db/models/options.py, modified
                # slightly since it's being run in ModelBase's prepare
                # rather than Options's (and, obviously, modified to add
                # a UUID rather than an ascending int).
                if opts.parents:
                    # Promote the first parent link in lieu of adding yet
                    # another field.
                    field = next(six.itervalues(opts.parents))

                    # Look for a local field with the same name as the first
                    # parent link. If a local field has already been created,
                    # use it instead of promoting the parent.
                    already_created = [fld for fld in opts.local_fields
                                       if fld.name == field.name]
                    if already_created:
                        field = already_created[0]
                    field.primary_key = True
                    opts.setup_pk(field)
                else:
                    from django_pg.models.fields.uuid import UUIDField
                    auto = UUIDField(auto_add=True, primary_key=True)
                    cls.add_to_class('id', auto)

        # Run the superclass method.
        # Note: We can't use `super` effectively here, because of some
        # subtleties of how six.with_metaclass works on Python 2.
        return models.base.ModelBase._prepare(cls)


class Model(six.with_metaclass(ModelBase, models.Model)):
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
            return models.Model.__repr__(self)

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
