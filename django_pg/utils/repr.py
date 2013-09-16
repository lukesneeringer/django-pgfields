from __future__ import absolute_import, unicode_literals


def smart_repr(obj, object_list=None, depth=1):
    """Return a repr of the object, using the object's __repr__ method.
    Be smart and pass the depth value if and only if it's accepted.
    """
    # If this object's `__repr__` method has a `__code__` object *and*
    #   the function signature contains `object_list` and `depth`, then
    #   include the object list.
    # Otherwise, just call the stock repr.
    if hasattr(obj.__repr__, '__code__'):
        if all([x in obj.__repr__.__code__.co_varnames
                for x in ('object_list', 'depth')]):
            return obj.__repr__(object_list=object_list, depth=depth)
    return repr(obj)
