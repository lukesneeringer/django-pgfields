from django.db import models
from django_pg.models.query import QuerySet


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