from collections import namedtuple
from datetime import date
from django.test import TestCase
from django_pg import models
from tests.composite.fields import Monarch, Book, Item
from tests.composite.models import Monarchy, Author, Character


class CompositeTestCase(TestCase):
    def setUp(self):
        """Create four Monarchy records, using different forms of
        construction.
        """
        Monarchy.objects.create(
            name='Gondor',
            ruler=Monarch(title='King', name='Elessar', suffix=2),
        )
        Monarchy.objects.create(
            name='Lothlórien',
            ruler=Monarch("H'Elf", 'Celeborn', 1),
        )
        Monarchy.objects.create(
            name='Rohan',
            ruler=('King', 'Théoden', 2),
        )
        Monarchy.objects.create(
            name='Erebor',
            ruler={
                'title': 'King',
                'name': 'Dain Ironfoot',
                'suffix': '2',
            },
        )

    def test_regular_lookup(self):
        """Test that a lookup by a non-Composite field works
        as expected on a model with one.
        """
        monarchy = Monarchy.objects.get(name='Gondor')
        self.assertEqual(monarchy.ruler.name, 'Elessar')
        self.assertEqual(monarchy.ruler.suffix, 2)

    def test_composite_lookup(self):
        """Test that a lookup on a CompositeField value works as expected."""
        monarchy = Monarchy.objects.get(ruler=Monarch(
            title='King',
            name='Théoden',
            suffix=2,
        ))
        self.assertEqual(monarchy.name, 'Rohan')

    def test_composite_lookup_tuple(self):
        """Test that a lookup on a CompositeField value using a tuple
        as the lookup value works as expected.
        """
        monarchy = Monarchy.objects.get(ruler=('King', 'Dain Ironfoot', 2))
        self.assertEqual(monarchy.name, 'Erebor')

    def test_composite_lookup_dict(self):
        """Test that a lookup on a CompositeField value using a dict as
        the lookup value works as expected.
        """
        monarchy = Monarchy.objects.get(ruler={
            'name': 'Elessar',
            'suffix': 2,
            'title': 'King',
        })
        self.assertEqual(monarchy.name, 'Gondor')

    def test_quoted_value(self):
        """Test that a quoted value is returned as expected."""
        monarchy = Monarchy.objects.get(name='Lothlórien')
        self.assertEqual(monarchy.ruler.title, "H'Elf")

    def test_invalid_lookup(self):
        """Test that a lookup other than `exact` raises TypeError."""
        with self.assertRaises(TypeError):
            Monarchy.objects.get(ruler__gt=5)

    def test_empty_composite(self):
        """Test that an empty composite field, instantiated from None,
        works as expected.
        """
        monarchy = Monarchy(name='The Grey Havens')
        self.assertEqual(monarchy.ruler.title, '')
        self.assertEqual(monarchy.ruler.suffix, 0)

    def test_invalid_composite_instance_init(self):
        """Test that if I send duplicate values to a CompositeInstance,
        that we raise the appropriate exception.
        """
        with self.assertRaises(TypeError):
            monarch = Monarch('King', title='King', name='Elessar', suffix=2)

    def test_invalid_composite_instance_key(self):
        """Test that an invalid composite instance key raises a KeyError
        as expected.
        """
        with self.assertRaises(KeyError):
            monarch = Monarch(title='King', label='Elessar', suffix=2)

    def test_related_field_raises(self):
        """Test that we cannot create a CompositeField subclass with
        any sort of RelatedField as a member.
        """
        with self.assertRaises(TypeError):
            class CitizenField(models.CompositeField):
                first_name = models.CharField(max_length=20)
                last_name = models.CharField(max_length=30)
                resident_of = models.ForeignKey(Monarchy)
        with self.assertRaises(TypeError):
            class CitizenField(models.CompositeField):
                first_name = models.CharField(max_length=20)
                last_name = models.CharField(max_length=30)
                authors = models.ManyToManyField(Author)


class ArrayCompositeTestCase(TestCase):
    def setUp(self):
        """Create multiple authors."""
        Author.objects.create(
            birthday=date(1898, 11, 29),
            books=[
                Book('The Lion, the Witch, and the Wardrobe', 320),
                Book(title='Prince Caspian', pages=340),
                ('The Voyage of the Dawn Treader', 290),
                { 'title': 'The Silver Chair', 'pages': 310 },
            ],
            name='C.S. Lewis',
            sex='male',
        )
        Author.objects.create(
            birthday=date(1892, 1, 3),
            books=[
                Book(title='The Fellowship of the Ring', pages=900),
                Book(title='The Two Towers', pages=800),
                Book(title='The Return of the King', pages=1050),
            ],
            name='J.R.R. Tolkien',
            sex='male',
        )

    def test_regular_lookup(self):
        """Access an author by a non-array/non-composite lookup."""
        author = Author.objects.get(name='J.R.R. Tolkien')
        self.assertEqual(author.sex, 'male')
        self.assertEqual(len(author.books), 3)

    def test_composite_containment_lookup_single(self):
        """Perform a lookup based on the existence of a single
        record within the composite type array.
        """
        book = Book('Prince Caspian', 340)
        author = Author.objects.get(books__contains=book)
        self.assertEqual(author.name, 'C.S. Lewis')

    def test_composite_containment_lookup_multi(self):
        """Perform a lookup based on the existance of two records
        within a composite type array, out of order.
        """
        books = [
            Book(title='The Return of the King', pages=1050),
            { 'title': 'The Fellowship of the Ring', 'pages': 900 },
        ]
        author = Author.objects.get(books__contains=books)
        self.assertEqual(author.name, 'J.R.R. Tolkien')


class NestedCompositeSuite(TestCase):
    """Test suite for nested composite fields."""

    def setUp(self):
        Character.objects.create(
            name='Gandalf',
            items=[
                Item(
                    name='Glamdring the Foe-hammer',
                    acquired_in=Book(
                        title='The Hobbit',
                        pages=600,
                    )
                )
            ]
        )
        Character.objects.create(
            name='Bilbo Baggins',
            items=[
                Item(name='The One Ring', acquired_in=('The Hobbit', 600)),
            ]
        )

    def test_nested_access(self):
        """Test that nested access for returned objects works."""

        character = Character.objects.get(name='Gandalf')
        self.assertEqual(character.items[0].acquired_in.title, 'The Hobbit')

    def test_nested_lookup(self):
        """Test that nested lookup works as expected."""

        character = Character.objects.get(
            items=[('Glamdring the Foe-hammer', ('The Hobbit', 600))],
        )
        self.assertEqual(character.name, 'Gandalf')


class CreateTypeSuite(TestCase):
    """Test suite for ensuring that the CREATE TYPE SQL comes out
    as expected.
    """
    def assertContains(self, haystack, needle):
        """Assert that `needle` is contained within `haystack`."""
        assert needle in haystack, '\n'.join((
            'Text not found within bigger block of text.\n',
            'Needle:',
            needle,
            '\nHaystack:',
            haystack,
        ))

    def test_simple_composite_sql(self):
        """Test that the simple case for returning create type
        SQL works.
        """
        from django.db import connection
        field = Monarchy._meta.get_field('ruler')
        sql = field.create_type_sql(connection)
        self.assertContains(sql, 'CREATE TYPE "monarch"')
        self.assertContains(sql, '"name" varchar(50)')
        self.assertContains(sql, '"suffix" integer')

    def test_array_composite_sql(self):
        """Test that composite SQL returns correctly for composite
        fields within arrays.
        """
        from django.db import connection
        field = Author._meta.get_field('books')
        sql = field.create_type_sql(connection)
        self.assertContains(sql, 'CREATE TYPE "book"')
        self.assertContains(sql, '"pages" integer')

    def test_nested_composite_sql(self):
        """Test that nested composite fields return appropriate
        CREATE TYPE SQL.
        """
        from django.db import connection



class SupportSuite(TestCase):
    """Test suite for support functions."""

    def test_field_names(self):
        """Test the function to return sub-field names from a
        composite field.
        """
        field = Monarchy._meta.get_field('ruler')
        self.assertEqual(field.field_names, ['title', 'name', 'suffix'])

    def test_composite_instance_repr(self):
        monarch_tuple_type = namedtuple(
            typename='Monarch',
            field_names=['title', 'name', 'suffix'],
        )

        monarch = Monarch(title='King', name='Elessar', suffix=2)
        monarch_tuple = monarch_tuple_type('King', 'Elessar', 2)
        self.assertEqual(repr(monarch), repr(monarch_tuple))
