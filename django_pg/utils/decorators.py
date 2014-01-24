from __future__ import absolute_import, unicode_literals
from functools import wraps


def validate_type(method):
    @wraps(method)
    def f(self, value):
        """Run the decorated method, and ensure that the return value
        is of the appropriate type.
        """
        # Run the decorated method.
        value = method(self, value)

        # If we don't have a type declared, then we're done;
        # return the value outright.
        if not self._type or isinstance(value, self._type):
            return value

        # This might be a "falsy" value.
        # 
        # If we have a falsy value, we don't want to be particularly picky
        # about the type; we just need to convert this to the equivalent
        # falsy value of the correct type.
        #
        # The use case for this particular situation is:
        # Say that the developer always wants to ensure that the value is
        # saved as a dictionary.  The value may be initialized through user
        # input (say, for instance, a value coming in through an API).
        # A form field would default to empty string, and so the value would
        # therefore be set to empty string, overriding the default.
        #
        # We don't want to throw an error in this situation; we simply wish
        # to ensure that we have a falsy value of the correct type, so
        # that code that consumes this value can safely assume that it will
        # always get a value of that type.
        if not value:
            return self._type()

        # Okay, we have a truthy value of the wrong type.
        #
        # Raise an exception in this case.  There are some cases where
        # it might coerce reasonably, but there are also lots of logic error
        # cases (such as coercing a dict to a list, which will work but
        # silently drop all the values).
        raise TypeError('Expected value of type %s; got %s' %
                        (self._type.__name__, type(value).__name__))
    return f
