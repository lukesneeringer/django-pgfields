Composite Fields
================

In addition to a generous set of built-in field types, PostgreSQL allows
for the definition of custom fields on a per-schema level. Composite fields
are simply custom fields that are composites of an ordered list of key names
and field types already provided by PostgreSQL.

Composite fields come with a few limitations compared to standard tables.
They can't have constraints of any kind, making them a poor choice for
anything requiring a foreign key. Similarly, if you're doing lookups based
on a composite field, you should know precisely what you're doing.

If you aren't familiar with PostgreSQL composite fields and want to understand
more about them, you should consult the PostgreSQL `composite fields
documentation`_ before continuing on.

Defining Composite Fields in the ORM
------------------------------------

The representation of composite fields in the ORM using django-pgfields
should be remarkably similar to the representation of models themselves,
since they're conceptually quite similar.

Differences from Model subclasses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A few things differ between models and composite fields:

* Composite fields inherit from ``django_pg.models.CompositeField`` rather
  than ``django.db.models.Model``.
* Composite fields do not get an ``id`` field by default, and do not need one.
* Composite fields may not contain any subclass of
  ``django.db.models.RelatedField``. This includes ``ForeignKey``,
  ``OneToOneField``, or ``ManyToManyField`` fields. 
* Any constraints provided to composite fields will be ignored at the
  database level.
  
    * Exception: ``max_length`` sent to ``CharField``. This is part of the
      type definition, and is still required.
* Most ``Meta`` options no longer have any meaning, and a new ``Meta``
  option (``db_type``) is available to composite fields.
* Composite fields can't do lookups based on a single key in the composite
  field. PostgreSQL has this ability, but it's not yet implemented in
  django-pgfields.

Type Definition Example
^^^^^^^^^^^^^^^^^^^^^^^

With these differences in mind, creating a composite field is straightfoward
and familiar::

    from django_pg import models

    class AuthorField(models.CompositeField):
        name = models.CharField(max_length=75)
        sex = models.CharField(max_length=6, choices=(
            ('male', 'Male'),
            ('female', 'Female'),
        ))
        birthdate = models.DateField()

Once the subclass is defined, it can be used within a model like any other
field::

    class Book(models.Model):
        title = models.CharField(max_length=50)
        author = AuthorField()
        date_published = models.DateField()

Meta Options
^^^^^^^^^^^^

**db_type**

All types in PostgreSQL have a name to identify them, such as ``text`` or
``int``. Your custom type must also have a name.

If you don't provide one, django-pgfields will introspect it from the name
of the class, by converting the class name to lower-case, and then stripping
off ``"field"`` from the end if it's present. So, in the example above,
our ``AuthorField`` would create an ``author`` type in the schema.

You may choose to provide one by specifying ``db_type`` in the field's
inner ``Meta`` class::

    class AuthorField(models.CompositeField):
        name = models.CharField(max_length=75)
        sex = models.CharField(max_length=6, choices=(
            ('male', 'Male'),
            ('female', 'Female'),
        ))
        birthdate = models.DateField()

        class Meta:
            db_type = 'ns_author'

Manual specification of the composite type's name is recommended, if only
so that they're namespaced (to a degree). You don't want your type name to
conflict with some new type that PostgreSQL may add in the future, after all.

Assigning Values to Composite Fields
------------------------------------

The presence of any composite field entails the need to write data to the
model instance containing that field. There are two ways to go about this:
by using a tuple, or by using a special "instance class" created when you
instantiate the field subclass.

Tuples
^^^^^^

In many simple circumstances, the quickest way to assign values is to use
a tuple. PostgreSQL accepts its write values to composite fields in a
tuple-like structure, with values provided in a specified order
(the order of the fields) and keys omitted.

This is a legal way to assign an author to a book::

    >>> hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
    >>> hobbit.author = ('J.R.R. Tolkien', 'male', date(1892, 1, 3))
    >>> hobbit.save()

Composite Instances
^^^^^^^^^^^^^^^^^^^

The above method works fine in simple cases, but isn't great for more complex
ones, especially since tuples are immutable. Fortunately, there's a solution.
Whenever a composite field is created, a "composite instance" class is
created alongside of it, and is available under the ``instance_class``
property of the field.

This example is identical in function to the tuple example shown above::

    >>> hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
    >>> hobbit.author = AuthorField.instance_class(
        birthdate=date(1892, 1, 3),
        name='J.R.R. Tolkien',
        sex='male',
    )
    >>> hobbit.save()

The actual name of the instance class is derived from the name of the field,
by dropping the name ``Field`` (if present) from the field name's subclass. If
the instance name does not conflict with the field name, it is automatically
assigned to the same module in which the instance was created.

In the above example, assuming that ``AuthorField`` was defined in the
``library.models`` module, we'd be able to do this::

    >>> from library.models import Book, Author
    >>> hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
    >>> hobbit.author = Author(
        birthdate=date(1892, 1, 3),
        name='J.R.R. Tolkien',
        sex='male',
    )
    >>> hobbit.save()

Accessing Composite Values
--------------------------

When values are being *read*, a composite instance is always used,
never a tuple. If a tuple is required, it can be explicitly typecast.

Composite values access *their* individual fields as attributes, just
like subclasses of Model::

    >>> hobbit = Book.objects.get(title='The Hobbit')
    >>> hobbit.author.name
    'J.R.R. Tolkien'
    >>> hobbit.author.birthdate
    date(1892, 1, 3)

.. _composite fields documentation: http://www.postgresql.org/docs/9.2/static/rowtypes.html
