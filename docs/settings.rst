Settings
========

django-pgfields provides several settings, which will customize its
operation.


DJANGOPG_CUSTOM_MANAGER
-----------------------

.. versionadded:: 1.0

* default: ``None``

django-pgfields 1.0 builds on previous versions of django-pgfields by
providing *two* Manager classes, one which subclasses the vanilla Django
Manager, and another which subclasses the GeoManager provided with Django's
GIS application, GeoDjango.

django-pgfields will automatically introspect which of these to use
by looking at the backend of the default database in your database settings.

However, if that result isn't what you want, or if you want a custom manager
to be applied across-the-board to all models that subclass
``django_pg.models.Model``, then set this to the particular Manager subclass
that you'd like.

You can do this by either providing the full module and class path as a
string, or by providing the class directly.


DJANGOPG_IMPROVED_REPR
----------------------

.. versionadded:: 1.0

* default: ``False``

Set this to ``True`` to enable the improved repr. Because providing an
alternate ``__repr__`` implementaiton is not the core function of
django-pgfields, it is offered on an opt-in basis.

See the `improved repr`_ documentation for more details.


DJANGOPG_REPR_TEMPLATE
----------------------

.. versionadded:: 1.0

* default: ``'single_line'``

Sets the template that is used by the improved repr provided by
django-pgfields. See the `improved repr`_ documentation for more details.

.. _improved repr: misc.html
