from __future__ import absolute_import, unicode_literals
from datetime import datetime
from django.db import models
from django.test.utils import override_settings
from django_pg.models import DateTimeField
import mock
import pytz
import unittest


class DateTimeFieldTests(unittest.TestCase):
    """Establish that our DateTimeField class works as expected."""

    @override_settings(USE_TZ=True)
    def test_int_with_use_tz(self):
        """Establish that if we send an integer to our datetime field
        subclass, that integers are accepted and return the value
        we expect.
        """
        dtf = DateTimeField()
        answer = dtf.to_python(1335024000)
        self.assertEqual(answer, datetime(2012, 4, 21, 16, tzinfo=pytz.UTC))

    @override_settings(USE_TZ=False, TIME_ZONE='UTC')
    def test_int_without_use_tz(self):
        """Establish that if we send an integer to our datetime field
        subclass, that integers are accepted and return the value
        we expect.
        """
        dtf = DateTimeField()
        answer = dtf.to_python(1335024000)
        self.assertEqual(answer, datetime(2012, 4, 21, 16))

    def test_passthrough(self):
        """Establish that we pass through non-integer values as
        expected.
        """
        dtf = DateTimeField()
        with mock.patch.object(models.DateTimeField, 'to_python') as tp:
            dtf.to_python('2012-04-21 16:00:00+0000')
            tp.assert_called_once_with('2012-04-21 16:00:00+0000')

    def test_get_prep_value(self):
        """Establish that the `to_python` method is called by
        `get_prep_value`.
        """
        dtf = DateTimeField()
        with mock.patch.object(DateTimeField, 'to_python') as tp:
            tp.return_value = datetime(2012, 4, 21, 16, tzinfo=pytz.UTC)
            dtf.get_prep_value(1335024000)

            # Starting in Django 1.7, there are actually two calls
            # to `to_python`, because `DateTimeField` has become a subclass of
            # `DateField`, and due to some internal esoteria each superclass
            # calls `to_python`.
            #
            # Since `to_python` is idempotent, this is fine, but it broke
            # the previous test that worked in 1.6 and below because that test
            # expected only a single call.
            #
            # In this case, we can just ensure that the first call to
            # `to_python` was, in fact, made with our timestamp argument,
            # and we don't have to be opinionated on whether the second call
            # happens or not.
            self.assertEqual(tp.mock_calls[0], mock.call(1335024000))
