Using django-pgfields
=====================

Using django-pgfields' extension to the Django ORM is fairly straightforward.
You don't need to use a custom backend (indeed, django-pgfields does not
provide one).

Instructions
------------

The short version of usage is that in order to use the features that
django-pgfields adds, you need to do two things.

Add django_pg to INSTALLED_APPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, you must add ``django_pg`` to your settings module's
``INSTALLED_APPS``::

    INSTALLED_APPS = [
        # your other apps
        'django_pg',
    ]

It doesn't matter where in the list you add it, as long as it's present.

from django_pg import models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Second, import django-pgfields' ``models`` module instead of the one
supplied by Django.

So, everywhere that you would write this::

    from django.db import models

Instead, write this::

    from django_pg import models

Internally, django-pgfields loads all of the things provided by the Django
``models`` module, subclassing certain items needed to make everything
work, and adding the fields it provides.

Explanation
-----------

Django provides a rich ORM with a valuable and customizable QuerySet API.
One aspect of this ORM is a high wall of separation between the use of data
in your application (such as the Python objects that are assigned to model
instance attributes) and the actual SQL that is generated to perform
operations, which additionally also changes to account for the fact that
Django ships with four backends (and several more are available).

One consequence of this design is that Field subclasses have a somewhat
restricted set of overridable bits. In particular, they can't (easily) touch
the representation of database field names or operators. This is
delegated to the backend and to a series of specialized classes which are
responsible for generating various pieces of the final SQL query.

The ultimate choreographer of this complex dance is the `Manager`_ class.
The ``Manager`` class instantiates the ``QuerySet`` class, which in turn
instantiates internal classes such as ``WhereNode`` and ``SQLExpression``
which are ultimately responsible for taking your querysets and constructing
actual queries suitable for your backend. Field classes have a very defined
(and limited) role in this dance, to avoid breaking down the wall between
the different segments of logic.

Complex fields like ``ArrayField`` and ``CompositeField`` are non-trivial,
and aren't use cases covered by Django's stock query construction classes.
Therefore, in order for them to function correctly, these classes must
be subclassed.

Importing your models module from django_pg instead of from django.db means
that you get django-pgfields' subclasses of ``Model`` and ``Manager``
which enable this extra functionality, as well as providing additional
(optional) hooks for other Field subclasses.

.. _Manager: https://docs.djangoproject.com/en/dev/topics/db/managers/
