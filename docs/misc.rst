=============
Miscellaneous
=============

Miscellaneous features provided by django-pgfields that are not actually
PostgreSQL-related fields.

Improved Repr
=============

.. versionadded:: 1.0

django-pgfields adds an optional, opt-in improved ``__repr__`` method
on the base Model class.

The default ``__repr__`` implementation on the Model class simply
identifies the model class to which the instance belonds, and does nothing
else::

    >>> mymodel = MyModel.objects.create(spam='eggs', foo='bar')
    >>> mymodel
    <MyModel: MyModel object>

The improved ``__repr__`` implementation that django-pgfields provides
iterates over the fields on the model and prints out a readable structure::

    >>> mymodel = MyModel.objects.create(spam='eggs', foo='bar')
    >>> mymodel
    <MyModel: { 'id': 1, 'spam': 'eggs', 'foo': 'bar' }>

This is more useful for debugging, logging, and working on the shell.

Settings
--------

django-pgfields exposes this functionality through optional settings in
your Django project.

**DJANGOPG_IMPROVED_REPR**

* default: ``False``

Set this to ``True`` to enable the improved repr. Because providing an
alternate ``__repr__`` implementaiton is not the core function of
django-pgfields, it is offered on an opt-in basis.


**DJANGOPG_REPR_TEMPLATE**

* default: ``'single_line'``

django-pgfields offers two built-in templates for printing model objects:
a single-line template and a multi-line template. They are the same, except
the model-line template adds line breaks and indentation for increased
readability. However, this readability may come at the expense of ease of
parsing logs.

* Set this to ``'single_line'`` for the single-line template (default).
* Set this to ``'multi_line'`` for the multi-line template.

The single-line template produces output like this::

    >>> mymodel = MyModel.objects.create(spam='eggs', foo='bar')
    >>> mymodel
    <MyModel: { 'id': 1, 'spam': 'eggs', 'foo': 'bar' }>

The multi-line template produces output like this::

    >>> mymodel = MyModel.objects.create(spam='eggs', foo='bar')
    >>> mymodel
    <MyModel: {
        'id': 1,
        'spam': 'eggs',
        'foo': 'bar'
    }>

Additionally, you may define your own template by providing a two-tuple
to this setting. Each tuple should be a string. The first string is the
overall template, and the second string is the glue on which the individual
fields are joined.

The template is populated using the `%` operator, and it is passed a
dictionary with four elements:

* ``class_name``: The name of the model class
* ``members``: The model's members, joined on the join glue
* ``tab``: The appropriate tab depth
* ``untab``: The appropriate tab depth for a depth one above; useful for
  closing off a structure

The glue is sent only the ``tab`` variable.
