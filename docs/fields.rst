Simple Fields
=============

django-pgfields exposes several new fields corresponding to data types
available in PostgreSQL that are not available in other databases
supported by Django.

These fields are available on the ``django_pg.models`` module
(see :doc:`usage` for more on this).

Array Field
-----------

PostgreSQL supports an array datatype. This is most similar to arrays in
many statically-typed languages such as C or Java, in that you explicitly
declare that you want an array of a specific type (for instance, an array
of integers or an array of strings).

django-pgfields exposes this by having the array field accept another field
as its initial argument (or, alternatively, by using the ``of`` keyword
argument).::

    from django_pg import models

    class Hobbit(models.Model):
        name = models.CharField(max_length=50)
        favorite_foods = models.ArrayField(models.CharField(max_length=100))
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)

This will create an array of strings in the database (to be precise:
``character varying(100) []``). Assignment of values is done using standard
Python lists::

    pippin = Hobbit.objects.create(
        name='Peregrin Took',
        favorite_foods=['apples', 'lembas bread', 'potatoes'],
    )

As a note, do not attempt to store a full list of any hobbit's favorite foods.
Your database server does not have sufficient memory or swap space for such
a list.

Lookups
^^^^^^^

When looking up data against an array field, the field supports three
lookup types: ``exact`` (implied), ``contains``, and ``len``.

**exact**

The ``exact`` lookup type is the implied lookup type when doing a lookup
in the Django ORM, and does not need to be explicitly specified. A straight
lookup simply checks for array equality. Continuing the example immediately
above::

    >>> hobbit = Hobbit.objects.get(
        favorite_foods=['apples', 'lembas bread', 'potatoes'],
    )
    >>> hobbit.name
    'Peregrin Took'

**contains**

The ``contains`` lookup type checks to see whether *all* of the provided
values exist in the array. If you only need to check for a single value,
and the value is not itself an array (in a nested case, for instance), you
may specify the lookup value directly::

    >>> hobbit = Hobbit.objects.get(favorite_foods__contains='apples')
    >>> hobbit.name
    'Peregrin Took'

If you choose to do a ``contains`` lookup on multiple values, then be aware
that *order is not relevant*. The database will check to ensure that each
value is present, but ignore order of values in the array altogether::

    >>> hobbit = Hobbit.objects.get(
        favorite_foods__contains=['lembas bread', 'apples'],
    )
    >>> hobbit.name
    'Peregrin Took'

**len**

The ``len`` lookup type checks the *length of* the array, rather than its
contents. It maps to the array_length_ function in PostgreSQL (with the second
argument set to ``1``).

Such lookups are simple and straightforward::

    >>> hobbit = Hobbit.objects.get(favorite_foods__len=3)
    >>> hobbit.name
    'Peregrin Took'


UUID Field
----------

In order to store UUIDs in the database under the PostgreSQL UUID type,
use the UUIDField field::

    from django_pg import models

    class Elf(models.Model):
        id = models.UUIDField(auto_add=True, primary_key=True)
        name = models.CharField(max_length=50)
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)

Options
^^^^^^^

The UUID field implements the following field options in addition to
the field options `available to all fields`_.

.. note::

    The UUID field interprets and writes blank values as SQL ``NULL``.
    Therefore, setting ``blank=True`` requires ``null=True`` also.
    Setting the former but not the latter will raise ``AttributeError``.


**auto_add**

Normally, the UUIDField works like any other Field subclass; you are
expected to provide a value, and the value is saved to the database directly.

If ``auto_add=True`` is set, then explicitly providing a value becomes
optional. If no value is provided, then the field will auto-generate a
random `version 4 UUID`_, which will be saved to the database (and assigned
to the model instance).

This is a particularly useful construct if you wish to store UUIDs for
primary keys; they're a completely acceptable substitute for auto-incrementing
integers::

    >>> legolas = Elf(name='Legolas Greenleaf')
    >>> legolas.id
    ''
    >>> legolas.save()
    >>> legolas.id
    UUID('b1f12115-3337-4ec0-acb9-1bcf63e44477')


Values
^^^^^^

The UUID field will return values from the database as Python `UUID`_
objects.

If you choose to do so, you may assign a valid string to the field. The
string will be converted to a ``uuid.UUID`` object upon assignment
to the instance::

    >>> legolas = Elf(name='Legolas Greenleaf')
    >>> legolas.id = '01234567-abcd-abcd-abcd-0123456789ab'
    >>> legolas.id
    UUID('01234567-abcd-abcd-abcd-0123456789ab')
    >>> type(legolas.id)
    <class 'uuid.UUID'>

Lookups can be performed using either strings or Python UUID objects.


.. _array_length: http://www.postgresql.org/docs/9.2/static/functions-array.html#ARRAY-FUNCTIONS-TABLE
.. _available to all fields: https://docs.djangoproject.com/en/dev/ref/models/fields/#field-options>`.
.. _version 4 UUID: http://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29
.. _UUID: http://docs.python.org/3/library/uuid.html
