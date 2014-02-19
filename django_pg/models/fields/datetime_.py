from datetime import datetime
from django.conf import settings
from django.db import models
from django_pg.utils.south import south_installed
import pytz


class DateTimeField(models.DateTimeField):
    """A DateTimeField subclass that knows how to convert an integer
    from a UNIX timestamp to a datetime.
    """
    def to_python(self, value):
        """If an integer is provided, return an appropriate datetime, assuming
        this is a UNIX Timestamp. Otherwise, run the superclass method.
        """
        if isinstance(value, int):
            if settings.USE_TZ:
                return datetime.fromtimestamp(value, tz=pytz.UTC)
            else:
                return datetime.fromtimestamp(value)
        return super(DateTimeField, self).to_python(value)


# If South is installed, then tell South how to properly
# introspect our DateTimeField subclass..
if south_installed:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([],
        (r'^django_pg\.models\.fields\.datetime_\.DateTimeField',),
    )
