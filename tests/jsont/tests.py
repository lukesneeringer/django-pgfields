from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django_pg.models.fields.json import JSONField
from tests.jsont.models import Song
import math


class JSONSuite(TestCase):
    """Test suite for testing the specialized JSON field."""

    def setUp(self):
        """Create test data."""

        Song.objects.create(
            title='Song of the Lonely Mountain',
            data={
                'sung_by': 'Dwarves',
                'verses': 10,
            },
            sample_lines=[
                'Far over the misty mountains cold,',
                'In dungeons deep, and caverns old,',
                'We must away, ere break of day,',
                'To seek the pale-enchanted gold.',
            ],
        )

        Song.objects.create(
            title="The Elves' Lullaby",
            data={
                'sung_by': 'Elves',
                'verses': 4,
            },
            sample_lines=[
                'Sing now ye joyful, now sing all together!',
                "The wind's in the tree-top, the wind's in the eather;",
                'The stars are in blossom, the moon is in flower,',
                'And bright are the windows of Night in her tower.',
            ],
            stuff=5,
        )

        Song.objects.create(
            title='All that is Gold does not Glitter',
            data={
                'written_by': 'Bilbo Baggins',
            },
            stuff='About Aragorn',
        )

        Song.objects.create(
            title='Chip the Glasses and Crack the Plates',
            sample_lines=[
                'Chip the glasses and crack the plates!',
                'Blunt the knives and bend the forks!',
                "That's what Bilbo Baggins hates-",
                'Smash the bottles and burn the corks!',
            ],
            stuff=6.8
        )

        Song.objects.create(
            title='O! What are you doing?',
            sample_lines=[
                'O! What are you doing,',
                'And where are you going?',
                'Your ponies need shoeing!',
                'The river is flowing!',
                'O! tra-la-la-lally here down in the valley!',
            ],
            stuff=True,
        )

    def test_list_access(self):
        """Test that I access an item saved as a list and it remains
        a list.
        """
        # Assert that a simple retreival on a list works.
        song = Song.objects.get(title='Song of the Lonely Mountain')
        self.assertEqual(song.sample_lines[0],
                                        'Far over the misty mountains cold,')

    def test_empty_list_default(self):
        """Test that accessing a field with an empty list as the default
        properly returns empty list.
        """
        # Assert that a retreival of a default value from a database
        # save returns what we expect. 
        song = Song.objects.get(title='All that is Gold does not Glitter')
        self.assertEqual(song.sample_lines, [])

    def test_creation_default_list(self):
        """Run an awkward test to ensure that setting default to
        empty list doesn't cross-contaminate models that use it.
        """
        # Assert that using a default list doesn't cross-contaminate.
        song1 = Song(title='The Long List of the Ents')
        song2 = Song(title='The Ent and the Entwife')
        song1.sample_lines.append('Learn now the Lore of Living Creatures!')
        self.assertEqual(song2.sample_lines, [])

    def test_ints(self):
        """Test that we get a value saved as an integer back
        as an integer.
        """
        # Test the save and load case.
        song = Song.objects.get(title="The Elves' Lullaby")
        self.assertEqual(song.stuff, 5)
        self.assertEqual(song.data, {
            'sung_by': 'Elves',
            'verses': 4,
        })

        # Test the assignment-as-string case.
        dummy = Song(stuff='8')
        self.assertEqual(dummy.stuff, 8)

    def test_floats(self):
        """Test that we get a value saved as a float back
        as a float.
        """
        # Test the save and load case.
        song = Song.objects.get(title='Chip the Glasses and Crack the Plates')
        self.assertEqual(song.stuff, 6.8)

        # Test the assignment-as-string-case.
        dummy = Song(stuff='42.7')
        self.assertEqual(dummy.stuff, 42.7)

    def test_bools(self):
        """Test that we get a value saved as a boolean back
        as a boolean.
        """
        # Test the save and load case.
        song = Song.objects.get(title='O! What are you doing?')
        self.assertEqual(song.stuff, True)

        # Test the assignment-as-string case.
        dummy = Song(stuff='false')
        self.assertEqual(dummy.stuff, False)

    def test_strs(self):
        """Test that we get a value saved as a string back
        as a string.
        """
        # Test the save and load case.
        song = Song.objects.get(title='All that is Gold does not Glitter')
        self.assertEqual(song.stuff, 'About Aragorn')

        # Test the assignment-within-JSON-string case.
        dummy = Song(stuff='"The Hobbit"')
        self.assertEqual(dummy.stuff, 'The Hobbit')

    def test_nones(self):
        """Test that we get a value saved as None back as None,
        and test that assigning null returns None.
        """
        # Test the save and load case.
        song = Song.objects.get(title='Song of the Lonely Mountain')
        self.assertEqual(song.stuff, None)

        # Test the assignment-as-string case.
        dummy = Song(stuff='null')
        self.assertEqual(dummy.stuff, None)

    def test_lookups(self):
        """Test that lookups raise TypeError, as PostgreSQL 9.2 does not
        support lookups of any kind on JSON fields.
        """
        with self.assertRaises(TypeError):
            Song.objects.get(stuff=5)
        with self.assertRaises(TypeError):
            Song.objects.get(stuff__contains={ 'verses': 10 })

    def test_invalid_assignment(self):
        """Establish that assignment of an invalid value to a JSON
        field raises ValidationError.
        """
        with self.assertRaises(TypeError):
            song = Song(sample_lines={'foo': 'bar'})

    def test_validation_falsy_coercion(self):
        """Establish that if we begin with a falsy value on a typed JSONField,
        that the value is converted to the correct type, and no error is
        raised.
        """
        song = Song(title='Something', sample_lines='')
        self.assertIsInstance(song.sample_lines, list)
        self.assertEqual(song.sample_lines, [])

class SupportSuite(TestCase):
    """Suite for testing more rarely-accessed aspects of JSON fields."""

    def test_invalid_type_assignment(self):
        """Establish that if we attempt to instantiate a JSONField
        with a type that doesn't readily serialize to JSON, that we
        raise TypeError.
        """
        with self.assertRaises(TypeError):
            JSONField(type=object)

    def test_empty_string_assign(self):
        """Test that assignment of empty string works as expected."""

        Song.objects.create(
            title='Fifteen Birds in Five Fir Trees',
            stuff='',
        )

        # Prove that the empty string is preserved when we get the
        # value back.
        song = Song.objects.get(title='Fifteen Birds in Five Fir Trees')
        self.assertEqual(song.stuff, '')

    def test_nan_and_inf(self):
        """Test that receipt of special JavaScript values are handled
        as they should be.
        """
        song = Song(
            title='Fifteen Birds in Five Fir Trees',
            stuff='{ "foo": NaN, "bar": Infinity }',
        )
        assert math.isnan(song.stuff['foo']), ' '.join((
            'Expected nan; got %r.' % song.stuff['foo'],
        ))
        assert math.isinf(song.stuff['bar']), ' '.join((
            'Expected inf; got %r.' % song.stuff['bar'],
        ))
