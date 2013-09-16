from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django.utils.unittest import skipIf
import django
import os


@skipIf('DJANGO_VERSION' not in os.environ, 'No target Django version.')
class VersionSuite(TestCase):
    """Establish that we are actually testing against the Django version
    that we think we're testing against.
    """
    def test_django_version(self):
        target = [int(i) for i in os.environ['DJANGO_VERSION'].split('.')]
        for expected, actual in zip(target, django.VERSION):
            self.assertEqual(expected, actual)
