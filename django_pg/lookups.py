from django.db.models import Lookup


class ArrayLength(Lookup):
    """A Lookup class that sends down appropriate SQL for a length
    check against a PostgreSQL array.
    """
    lookup_name = 'len'

    def as_sql(self, qn, connection):
        """Return appropriate SQL for an array length lookup
        in PostgreSQL.
        """
        # Get the name of the field and the value that was sent.
        field = qn.compile(self.lhs)[0]
        value = self.rhs

        # Return the appropriate SQL.
        if value:
            return '%s = ARRAY_LENGTH({0}, 1)'.format(field), (value,)
        return 'ARRAY_LENGTH({0}, 1) IS NULL'.format(field), ()


class ArrayContains(Lookup):
    """A Lookup class that sends down appropriate SQL for a membership
    check against a PostgreSQL array.
    """
    lookup_name = 'contains'

    def as_sql(self, qn, connection):
        """Return appropriate SQL for an array contains lookup
        in PostgreSQL.
        """
        # Get the name of the field and the value that was sent.
        field = qn.compile(self.lhs)[0]
        value = self.rhs
        db_type = self.field.db_type(connection)

        # Return the appropriate SQL.
        if isinstance(value, (list, tuple)):
            return '{0}::{1} @> %s::{1}'.format(field, db_type), (value,)
        return '%s = ANY({0}::{1})'.format(field, db_type), (value,)


class ArrayExact(Lookup):
    """A Lookup class that sends down the appropriate SQL for an equality
    check against a PostgreSQL array.
    """
    lookup_name = 'exact'

    def as_sql(self, qn, connection):
        """Return appropriate SQL for an array contains lookup
        in PostgreSQL.
        """
        # Get the name of the field and the value that was sent.
        field = qn.compile(self.lhs)[0]
        value = self.rhs
        db_type = self.field.db_type(connection)

        # Return the appropriate SQL.
        return '{0} = %s::{1}'.format(field, db_type), (value,)
