from __future__ import absolute_import, unicode_literals


class CoerciveList(list):
    """List subclass that coerces every element in the list
    to an appropriate type.
    """
    def __init__(self, coerce, iterable=None):
        """Initialize the coercive list, saving the field class that
        knows how to do the coercison, as well as any list sent.
        """
        super(CoerciveList, self).__init__()
        self.coerce = coerce
        if iterable:
            self.extend(iterable)

    def __copy__(self):
        """Create a copy of this list."""
        return self.__class__(self.coerce, self)

    def __repr__(self):
        return super(CoerciveList, self).__repr__()

    def append(self, item):
        item = self.coerce(item)
        super(CoerciveList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def insert(self, index, item):
        item = self.coerce(item)
        super(CoerciveList, self).insert(index, item)
