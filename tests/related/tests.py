from __future__ import absolute_import, unicode_literals
from tests.related.models import Moogle, Letter
from django.test import TestCase


class SelectRelatedTests(TestCase):
    """Establish that the `select_related` Meta option works as expected,
    and that `get_queryset` correctly returns a queryset with the
    appropriate `select_related` call made.
    """
    def test_selrel_str(self):
        """Establish that when a single `select_related` is specified
        in `Meta` as a string, that we do the right thing.
        """
        qs = Moogle.objects.all()
        self.assertIn('game', qs.query.select_related)        

    def test_selrel_iterable(self):
        """Establish that when a `select_related` is specified as an
        iterable, such as a list, that the appropriate `select_related`
        call is made.
        """
        qs = Letter.objects.all()
        for rel_field in ('game', 'moogle'):
            self.assertIn(rel_field, qs.query.select_related)
