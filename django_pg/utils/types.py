from __future__ import absolute_import, unicode_literals


# Taken from the following StackOverflow answer:
#   http://stackoverflow.com/a/3703727/199176
SELECT_TYPES_SQL = """
    SELECT n.nspname as schema, t.typname as type 
      FROM pg_type t 
 LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
     WHERE (t.typrelid = 0 OR (
            SELECT c.relkind = 'c'
              FROM pg_catalog.pg_class c
             WHERE c.oid = t.typrelid)
           ) 
       AND NOT EXISTS(
            SELECT 1 
              FROM pg_catalog.pg_type el
             WHERE el.oid = t.typelem
               AND el.typarray = t.oid
           )
       AND n.nspname NOT IN ('pg_catalog', 'information_schema')
"""


def get_type_names(connection):
    """Return a list of custom types currently defined and visible
    to the application in PostgreSQL.
    """
    cursor = connection.cursor()
    cursor.execute(SELECT_TYPES_SQL)
    rows = cursor.fetchall()
    return set([i[1] for i in rows])


def type_exists(connection, type_name):
    """Return True if the given PostgreSQL type exists, False otherwise."""
    type_name = type_name.lower()
    return type_name in get_type_names(connection)
