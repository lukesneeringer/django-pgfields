from django.core.management import call_command
from django.test import TestCase
from django.utils.unittest import skipIf
from django_pg.utils.context import redirect_std
from django_pg.utils.south import south_installed


@skipIf(not south_installed, 'South is not installed.')
class SouthSuite(TestCase):
    """A test case for the creation of South migrations."""

    def test_migration_creation(self):
        """Test that I can create a migration with all of my
        custom fields.
        """
        # Fake the creation of a migration.
        # The '-' argument to `schemamigration` sends the migration
        #   to stdout rather than actually creating a real migration.
        with redirect_std() as std:
            call_command('schemamigration', 'south_migrations', '-', auto=True)
            out = std['out'].getvalue()

        # Define values that I expect.
        # Sadly, there's no pretty way to do this.
        needles = {
            "'books':": (
                "'django_pg.models.fields.array.ArrayField', [], {'of': ",
                "\"SchemaMigration.gf(None, 'tests.composite.fields.BookField')()\"}),",
            ),
            "'uuid':": (
                "('django_pg.models.fields.uuid.UUIDField', [], {",
                "'null': 'True'",
            ),
            "db.add_column('south_migrations_author', 'uuid',": (
                "self.gf('django_pg.models.fields.uuid.UUIDField')(",
                "null=True",
                "keep_default=False",
            ),
            "db.add_column('south_migrations_author', 'books',": (
                "self.gf('django_pg.models.fields.array.ArrayField')(",
                "of=SchemaMigration.gf(None, 'tests.composite.fields.BookField')()",
                "keep_default=False",
            ),
        }

        # Assert that each of my expected migration blocks does,
        # in fact, exist.
        for anchor, sub_needles in needles.items():
            # Each key should exist in the output. If it doesn't,
            # we have a different problem.
            assert anchor in out, 'Could not find: %s' % item

            # Each needle in the value tuple should also be present,
            # and should be present shortly after the anchor. 
            index = out.index(anchor) + len(anchor)
            for needle in sub_needles:
                assert needle in out[index:index + 200], ' '.join((
                    'Could not find', needle, 'near', anchor
                ))
