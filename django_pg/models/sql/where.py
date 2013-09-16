from __future__ import absolute_import, unicode_literals
from django.db.models.sql import where
from django_pg.utils.gis import gis_backend

if gis_backend:
    from django.contrib.gis.db.models.sql import where as gis_where


class WhereMixin(object):
    """Mixin for where node classes, which teaches them
    how to perform PostgreSQL-specific operations added in django_pg.
    """
    def make_atom(self, child, qn, connection):
        lvalue, lookup_type, value_annot, params_or_value = child

        # If the lookup type's behavior is defined by the Field subclass,
        # then we want to make sure the Field's behavior is honored
        # in lieu of the regular processing.
        if isinstance(lvalue, where.Constraint):
            field = lvalue.field

            # Process the value side first.
            lvalue, params = lvalue.process(
                connection=connection,
                lookup_type=lookup_type,
                value=params_or_value
            )

            # Sanity check: The processing of the value might change it to
            #   None, if this is a new custom lookup type that Constraint
            #   does not define.
            # Rather than subclassing Constraint just to overwrite this
            #   behavior, I can simply intercept None and make it into
            #   a one-dimensional list containing the value we got before,
            #   which is what Django expects (`get_db_prep_lookup` consistently
            #   returns a list).
            if params is None:
                params = [params_or_value]

            # If there is a `get_db_lookup_expression` method on the field,
            # then use that to determine the SQL expression in lieu of the
            # Django stock processing.
            if hasattr(field, 'get_db_lookup_expression'):
                expr = field.get_db_lookup_expression(
                    connection=connection,
                    lookup_type=lookup_type,
                    value=params_or_value,
                )

                # If the field subclass doesn't actually define
                #   what should be done for this lookup type, it will
                #   return None.
                # If we have anything other than None, we should be done.
                if expr:
                    return (
                        expr.format(
                            field=self.sql_for_columns(lvalue, qn, connection),
                            value='%s',
                        ),
                        params,
                    )

            # Use the superclass logic to handle this; it's a "normal" case.
            return super(WhereMixin, self).make_atom(
                child=child,
                connection=connection,
                qn=qn,
            )


class WhereNode(WhereMixin, where.WhereNode):
    pass

if gis_backend:
    class GeoWhereNode(WhereMixin, gis_where.GeoWhereNode):
        pass
