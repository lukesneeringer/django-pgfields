from django.test import TestCase
from django_pg import models
from django_pg.models.fields.uuid import UUIDAdapter, UUIDField
from tests.uuid_.models import Movie, Game, Book
import uuid


class UUIDAutoSuite(TestCase):
    """Test suite for auto UUID fields (those with `auto_add=True`)."""

    def setUp(self):
        """Create several movie objects, establishing that object creation
        works for the custom UUID field.
        """
        Movie.objects.create(title='The Fellowship of the Ring')
        Movie.objects.create(title='The Two Towers')
        Movie.objects.create(
            id='01234567-0123-0123-0123-0123456789ab',
            title='The Return of the King',
        )

    def test_specified_uuid(self):
        """Test that the specified UUID record works as expected."""
        movie = Movie.objects.get(title='The Return of the King')
        self.assertEqual(str(movie.id), '01234567-0123-0123-0123-0123456789ab')

    def test_random_uuid(self):
        """Test that we get a random UUID back when we choose
        not to explicitly specify one.
        """
        movie = Movie.objects.get(title='The Two Towers')
        assert isinstance(movie.id, uuid.UUID), ( 'Expected UUID, got %s.' %
                                                movie.id.__class__.__name__ )
        tt_uuid = str(movie.id)
        self.assertEqual(tt_uuid[14], '4')
        assert tt_uuid[19] in ('8', '9', 'a', 'b'), 'Invalid random UUID.'

    def test_uuid_retreival_str(self):
        """Test retreival by UUID-like string."""
        movie = Movie.objects.get(id='01234567-0123-0123-0123-0123456789ab')
        self.assertEqual(movie.title, 'The Return of the King')

    def test_uuid_retreival_uuid(self):
        """Test retreival by UUID object."""
        movie = Movie.objects.get(id=uuid.UUID(
            '01234567-0123-0123-0123-0123456789ab',
        ))
        self.assertEqual(movie.title, 'The Return of the King')


class UUIDManualSuite(TestCase):
    """Test suite for manual UUID fields (those without `auto_add=True`)."""

    def setUp(self):
        """Create a game object, establishing that object creation
        works for a regular UUID field.
        """
        Game.objects.create(
            title='Lego Lord of the Rings',
            uuid='abcdabcd-abcd-abcd-abcd-abcdabcdabcd',
        )
        Game.objects.create(
            title='Lego The Hobbit',
            uuid=uuid.uuid1(),
        )

    def test_uuid_retreival(self):
        """Test retreival by UUID."""
        game = Game.objects.get(uuid='abcdabcd-abcd-abcd-abcd-abcdabcdabcd')
        self.assertEqual(game.title, 'Lego Lord of the Rings')

    def test_uuid_none(self):
        """Establish that trying to save a non-auto-adding UUID fails
        if no UUID is provided and null=False.
        """
        with self.assertRaises(ValueError):
            Game.objects.create(
                title='Lego Batman',
            )

    def test_uuid_assignment(self):
        """Establish that assigning a UUID as a string converts the
        value to uuid.UUID."""
        game = Game()
        game.uuid = '01234567-abcd-abcd-abcd-0123456789ab'
        assert isinstance(game.uuid, uuid.UUID), 'Value should be a UUID.'

class NullUUIDSuite(TestCase):
    """Ensure that behavior around nullable UUID fields functions
    as expected.
    """
    def test_uuid_null(self):
        book = Book.objects.create(title='The Hobbit')
        self.assertEqual(book.uuid, None)

    def test_uuid_null_blank_error(self):
        """Ensure that we cannot instantiate a UUIDField with blank=True
        but not null=True.
        """
        with self.assertRaises(AttributeError):
            class Thing(models.Model):
                uuid = models.UUIDField(blank=True)


class SupportSuite(TestCase):
    """Test support classes."""

    def test_uuid_adapter(self):
        """Ensure that the UUIDAdapter object will fail if it receives
        something other than a `uuid.UUID` object.
        """
        with self.assertRaises(TypeError):
            adapter = UUIDAdapter('01234567-0123-0123-0123-0123456789ab')
