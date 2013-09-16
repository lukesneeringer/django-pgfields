Welcome to django-pgfields
==========================

This is django-pgfields, a pluggable Django application that adds support
for several specialized PostgreSQL fields within the Django ORM.

django-pgfields will work with Django applications using the PostgreSQL
backend, and adds support for:

* Arrays
* Composte Types
* JSON
* UUIDs

Dependencies & Limitations
--------------------------

django-pgfields depends on:

* Python 2.7+ or 3.3+ (Python 2.6 probably works, but is not explicitly tested against.)
* Django 1.5+
* Psycopg2 2.5+
* six 1.4.1+


Quick Start
-----------

In order to use django-pgfields in a project:

* Installation
    * ``pip install django-pgfields``
    * Add ``django_pg`` to your ``settings.INSTALLED_APPS``.
* Usage
    * Essentially: Import our models module instead of the stock Django module.
      So, replace ``from django.db import models`` with
      ``from django_pg import models``.
    * The new field classes provided by ``django_pg`` are now available
      on the models module. Use, for instance, ``models.UUIDField`` and
      ``models.ArrayField`` just as you would use ``models.CharField``.


Getting Help
------------

If you think you've found a bug in django-pgfields itself, please post an
issue on the `Issue Tracker`_.

For usage help, you're free to e-mail the author, who will provide help (on
a best effort basis) if possible.


License
-------

New BSD.


Index
-----

.. toctree::
    :maxdepth: 2

    usage
    fields
    composite
    misc
    settings
    releases/index

.. _Issue Tracker: https://github.com/lukesneeringer/django-pgfields/issues
