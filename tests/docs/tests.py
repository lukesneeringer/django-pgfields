from datetime import date
from django.test import TestCase
from tests.docs.models import Hobbit, Elf, Author, AuthorField, Book
import uuid


class TestArrayDocs(TestCase):
    """Test suite for testing sample code in the documentation provided
    for ArrayField.
    """
    def setUp(self):
        """Create a single hobbit in the database, which is the basis
        for other provided examples.
        """
        pippin = Hobbit.objects.create(
            name='Peregrin Took',
            favorite_foods=['apples', 'lembas bread', 'potatoes'],
        )

    def test_lookup_exact(self):
        """Establish that the `exact` lookup works as documented."""

        # Test the implicit method (which is the one everyone will
        # actually use).
        hobbit = Hobbit.objects.get(
            favorite_foods=['apples', 'lembas bread', 'potatoes'],
        )
        self.assertEqual(hobbit.name, 'Peregrin Took')

        # Test the explicit way, because it's explicitly documented.
        hobbit = Hobbit.objects.get(
            favorite_foods__exact=['apples', 'lembas bread', 'potatoes'],
        )
        self.assertEqual(hobbit.name, 'Peregrin Took')

    def test_lookup_contains(self):
        """Establish that the `contains` lookup works as documented."""

        # Test a single-item containment lookup.
        hobbit = Hobbit.objects.get(favorite_foods__contains='apples')
        self.assertEqual(hobbit.name, 'Peregrin Took')

        # Test a multiple-item containment lookup.
        hobbit = Hobbit.objects.get(
            favorite_foods__contains=['lembas bread', 'apples'],
        )
        self.assertEqual(hobbit.name, 'Peregrin Took')

    def test_lookup_len(self):
        """Establish that the `len` lookup works as documented."""

        hobbit = Hobbit.objects.get(favorite_foods__len=3)
        self.assertEqual(hobbit.name, 'Peregrin Took')


class TestUUIDDocs(TestCase):
    """Test suite for testing sample code in the documentation provided
    for UUIDField.
    """
    def test_save(self):
        """Estblish that UUIDs are automatically created as documented."""
        legolas = Elf(name='Legolas Greenleaf')
        self.assertEqual(legolas.id, '')
        legolas.save()
        assert isinstance(legolas.id, uuid.UUID)

    def test_manual_assignment(self):
        """Establish that manual UUID assignment works as documented."""
        legolas = Elf(name='Legolas Greenleaf')
        legolas.id = '01234567-abcd-abcd-abcd-0123456789ab'
        self.assertEqual(
                legolas.id, uuid.UUID('01234567-abcd-abcd-abcd-0123456789ab'))
        self.assertEqual(type(legolas.id), uuid.UUID)


class TestCompositeDocs(TestCase):
    """Test suite for testing sample code provided in the composite field
    documentation.
    """
    def test_tuple_assignment(self):
        """Establish that we can assign composite fields by tuple as shown
        in the example documentation.
        """
        hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
        hobbit.author = ('J.R.R. Tolkien', 'male', date(1892, 1, 3))
        hobbit.save()

    def test_instance_class_assignment_by_field_access(self):
        """Establish that we can assign composite fields using the
        CompositeField.instance_class paradigm.
        """
        hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
        hobbit.author = AuthorField.instance_class(
            birthdate=date(1892, 1, 3),
            name='J.R.R. Tolkien',
            sex='male',
        )
        hobbit.save()

    def test_instance_class_assignment_by_module_access(self):
        """Establish that we can assign composite fields using the
        paradigm of pulling the composite instance subclass from the same
        module.
        """
        hobbit = Book(title='The Hobbit', date_published=date(1937, 9, 21))
        hobbit.author = Author(
            birthdate=date(1892, 1, 3),
            name='J.R.R. Tolkien',
            sex='male',
        )
        hobbit.save()

    def test_instance_class_access(self):
        """Estblish that instance class access works the way the
        documentation claims.
        """
        # First, create the book.
        Book.objects.create(
            author=Author(
                birthdate=date(1892, 1, 3),
                name='J.R.R. Tolkien',
                sex='male',
            ),
            date_published=date(1937, 9, 21),
            title='The Hobbit',
        )

        # Now access the book and test the attributes the way the
        # documentation explains.
        hobbit = Book.objects.get(title='The Hobbit')
        self.assertEqual(hobbit.author.name, 'J.R.R. Tolkien')
        self.assertEqual(hobbit.author.birthdate, date(1892, 1, 3))

