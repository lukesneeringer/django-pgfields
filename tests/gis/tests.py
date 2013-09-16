from __future__ import absolute_import, unicode_literals
from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase
from django.utils.unittest import skipIf
from django_pg.utils.gis import gis_backend
if gis_backend:
    from tests.gis.models import Place


@skipIf(not gis_backend, 'GIS backend not in use.')
class QuerySuite(TestCase):
    """Test suite establishing that we are able to run both geo queries
    and django_pg queries.
    """
    def setUp(self):
        Place.objects.create(
            name='The Shire',
            books=[
                'The Hobbit',
                'The Fellowship of the Ring',
                'The Two Towers',
                'The Return of the King',
            ],
            bounds=Polygon((
                (0.0, 0.0),
                (0.0, 50.0),
                (50.0, 50.0),
                (50.0, 0.0),
                (0.0, 0.0),
            )),
        )

    def test_array_query(self):
        """Establish that an array query still works when using our
        GeoManager object.
        """
        place = Place.objects.get(books__contains='The Hobbit')
        self.assertEqual(place.name, 'The Shire')
        place = Place.objects.get(books__len=4)
        self.assertEqual(place.name, 'The Shire')

    def test_geo_query(self):
        """Establish that a geo query still works when using our
        GeoManager object.
        """
        place = Place.objects.get(bounds__bbcontains=Point(25, 25))
        self.assertEqual(place.name, 'The Shire')
