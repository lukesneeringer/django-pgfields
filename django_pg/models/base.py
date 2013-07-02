from django.conf import settings
from django.db import models
from django.db.models import options
from django_pg.models.query import QuerySet
from django_pg.utils.repr import smart_repr


# This is a monkey patch on `django.db.models.options.Options`.
# Adding these two default values allow them as values in Meta inner-classes.
if getattr(settings, 'DJANGOPG_IMPROVED_REPR', False):
    options.DEFAULT_NAMES = (options.DEFAULT_NAMES +
                             ('repr_fields', 'repr_fields_exclude'))


class Manager(models.Manager):
    """Base model class, which extends Django's ORM with the
    necessary extensions.
    """
    # It's completely fine to use our custom manager for related fields,
    # and it's necessary, since we need to ensure that our custom queries
    # and query sets are what are created throughout.
    use_for_related_fields = True

    def get_queryset(self):
        return QuerySet(self.model, using=self._db)

    def get_query_set(self):
        return self.get_queryset()


class Model(models.Model):
    """Base model class for `django_pg`, which extends Django's ORM
    with PostgreSQL-specific extensions.
    """
    objects = Manager()

    class Meta:
        abstract = True

    def __repr__(self, object_list=None, depth=1):
        """Send down a useful, unambiguous representation of the
        object.
        """
        # Sanity check: Is our improved repr system turned on?
        # If it's not turned on, don't use it: this is an explicit opt-in.
        if not getattr(settings, 'DJANGOPG_IMPROVED_REPR', False):
            return super().__repr__()

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
            field_names = [i.name for i in self._meta._fields()]
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
        if isinstance(template, str):
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
