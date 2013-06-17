from django.test import TestCase
from tests.arrays.models import Place


class ArrayTests(TestCase):
    def setUp(self):
        """Create objects in the database, effectively establishing
        that we can save items.
        """
        Place.objects.create(name='Rivendell', residents=['Elrond'])
        Place.objects.create(name='Gondor', residents=['Aragorn', 'Denethor'])
        Place.objects.create(name='The Shire', residents=[
            'Bilbo Baggins', 'Frodo Baggins', 'Samwise Gamgee',
            'Peregrin Took', 'Merridoc Brandybuck',
        ])
        Place.objects.create(name='Rohan', residents=[
            'Théoden', 'Éomer', 'Éowyn',
        ])
        Place.objects.create(name='Mordor', residents=[])

    def test_traditional_lookup(self):
        """Establish that we can retreive a record another field, and that
        array values come through as we expect.
        """
        place = Place.objects.get(name='Rivendell')
        self.assertEqual(place.residents, ['Elrond'])

    def test_array_lookup_exact(self):
        """Establish that we can retreive a record by a full array field,
        and that the array comes through as expected.
        """
        place = Place.objects.get(residents=['Aragorn', 'Denethor'])
        self.assertEqual(place.name, 'Gondor')

    def test_array_lookup_contains_one(self):
        """Establish that we can retreive a record by checking containment
        of an individual item.
        """
        place = Place.objects.get(residents__contains='Frodo Baggins')
        self.assertEqual(place.name, 'The Shire')

    def test_array_lookup_contains_multi(self):
        """Establish that we can retreive a record by checking containment
        of multiple items.
        """
        place = Place.objects.get(residents__contains=[
            'Merridoc Brandybuck', 'Peregrin Took',
        ])
        self.assertEqual(place.name, 'The Shire')

    def test_array_lookup_special_chars(self):
        """Establish that this still works when interesting characters
        are involved.
        """
        place = Place.objects.get(residents__contains='Éowyn')
        self.assertEqual(place.name, 'Rohan')

    def test_array_lookup_len(self):
        place = Place.objects.get(residents__len=5)
        self.assertEqual(place.name, 'The Shire')

    def test_invalid_lookup_type(self):
        """Establish that an invalid lookup type raises the expected
        exception.
        """
        with self.assertRaises(TypeError):
            place = Place.objects.get(residents__gt=5)

    def test_invalid_len_lookup(self):
        """Establish that attempting a `len` lookup with something
        other than an integer fails in the expected way.
        """
        with self.assertRaises(TypeError):
            place = Place.objects.get(residents__len='foo')

    def test_empty_array(self):
        place = Place.objects.get(name='Mordor')
        self.assertEqual(place.residents, [])

    def test_create_type_sql(self):
        """Establish that, on an array of a standard field type,
        we return back an empty string for create_type_sql.
        """
        from django.db import connection
        field = Place._meta.get_field('residents')
        self.assertEqual(field.create_type_sql(connection), '')
