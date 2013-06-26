from django.core.management import call_command
from django.test import TestCase
from django.utils.unittest import skipIf
from django_pg.utils.context import redirect_std
from django_pg.utils.south import south_installed


@skipIf(not south_installed, 'South is not installed.')
class MigrationCreationSuite(TestCase):
    """A test case for the creation of South migrations."""

    def setUp(self):
        """Fake the creation of a migration, and store the migration
        contents to test against.
        """
        # The '-' argument to `schemamigration` sends the migration
        # to stdout rather than actually creating a real migration.
        with redirect_std() as std:
            call_command('schemamigration', 'south_migrations', '-', auto=True)
            self.migration_code = std['out'].getvalue()

    def test_array_freeze(self):
        """Test that array migrations are frozen as I expect."""

        self.find_in_migration("'books':", (
            "'django_pg.models.fields.array.ArrayField', [], {'of': ",
            ''.join((
                "\"SchemaMigration.gf(None, 'tests.composite.",
                "fields.BookField')()\"}),",
            )),
        ))

    def test_array_forwards(self):
        """Test that the creation of an ArrayField in the forwards
        migration appears to be valid code.
        """
        self.find_in_migration(
            "db.add_column('south_migrations_author', 'books',",
            (
                "self.gf('django_pg.models.fields.array.ArrayField')(",
                ''.join((
                    "of=SchemaMigration.gf(None, 'tests.composite.",
                    "fields.BookField')()",
                )),
                "keep_default=False",
            ),
            distance=200,
        )

    def test_json_freeze(self):
        """Test that JSON fields are frozen as I expect."""

        self.find_in_migration("'data':", (
            "('django_pg.models.fields.json.JSONField', [], {",
        ))

    def test_json_forwards(self):
        """Test that JSON fields are given valid representations
        in the forwards method of migrations.
        """

        self.find_in_migration(
            "db.add_column('south_migrations_author', 'data',",
            (
                "self.gf('django_pg.models.fields.json.JSONField')(",
                "keep_default=False",
            ),
            distance=150,
        )

    def test_uuid_freeze(self):
        """Test that UUID fields are frozen as I expect."""

        self.find_in_migration("'uuid':", (
            "('django_pg.models.fields.uuid.UUIDField', [], {",
            "'null': 'True'",
        ))

    def test_uuid_forwards(self):
        """Test that UUID fields are given valid representations
        in the forwards method of migrations.
        """

        self.find_in_migration(
            "db.add_column('south_migrations_author', 'uuid',",
            (
                "self.gf('django_pg.models.fields.uuid.UUIDField')(",
                "null=True",
                "keep_default=False",
            ),
            distance=150,
        )


    def find_in_migration(self, anchor, needles, terminus='\n', distance=None):
        """Assert the presence of the given anchor in the output.

        Once the anchor is found, assert the presence of *each* provided
        needle within bounds. If `terminus` is provided, each needle must
        appear before the next instance of `terminus`.

        If `distance` is provided, each needle must appear within `distance`
        characters, and `terminus` is ignored.
        """

        # The anchor must exist. If it doesn't, we have another problem.
        assert anchor in self.migration_code, 'Could not find: %s' % anchor
        start = self.migration_code.index(anchor) + len(anchor)

        # If a distance is provided, get the substring based on it.
        # Otherwise, use the terminus.
        if distance:
            block = self.migration_code[start:start + distance]
        else:
            try:
                end = self.migration_code.index(terminus, start)
            except ValueError:
                end = None
            block = self.migration_code[start:end]

        # Assert that each of my expected needles is found in the
        # given haystack.
        for needle in needles:
            assert needle in block, 'Could not find text:\n%s' % needle
