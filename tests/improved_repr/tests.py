from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django.test.utils import override_settings
from tests.improved_repr.models import (Book, Movie, Publisher, Character,
                                        Interview, Studio)
import re


class BasicReprSuite(TestCase):
    """Test case establishing that my basic repr improvements work
    as expected.
    """
    def setUp(self):
        # What model is being tested?
        self._testing_model = Book

        # Create the model instance.
        Book.objects.create(
            title='The Hobbit',
            year_published=1937,
        )

    @override_settings(DJANGOPG_IMPROVED_REPR=False)
    def test_unimproved_repr(self):
        instance = self._testing_model.objects.all()[0]
        self.assertEqual(repr(instance), '<{0}: {0} object>'.format(
            self._testing_model.__name__,
        ))

    @override_settings(DJANGOPG_REPR_TEMPLATE='single_line')
    def test_single_line_repr(self):
        instance = self._test_improved_repr()
        assert '\n' not in repr(instance), 'Expected no line breaks.'
        return instance

    @override_settings(DJANGOPG_REPR_TEMPLATE='multi_line')
    def test_multi_line_repr(self):
        instance = self._test_improved_repr()
        assert '\n' in repr(instance), 'Expected line breaks; found none.'
        return instance

    def _test_improved_repr(self):
        instance = self._testing_model.objects.all()[0]
        for key in [i.name for i in self._testing_model._meta.fields]:
            # Determine whether this repr item accepts depth.
            # If it does, send depth of 2; otherwise, do nothing.
            field_value = getattr(instance, key)
            value = repr(field_value)
            if hasattr(field_value.__repr__, '__code__'):
                if all([i in field_value.__repr__.__code__.co_varnames
                        for i in ('depth', 'object_list')]):
                    value = field_value.__repr__(
                        depth=2,
                        object_list=[instance],
                    )

            # The values should now match.
            assert '%r: %s' % (key, value) in repr(instance), '%s, %s, %s' % (
                key, value, instance
            )
        return instance


class ForeignKeyReprSuite(BasicReprSuite):
    """Test case establishing that my repr improvements work when
    a model with a foreign key is introduced.
    """
    def setUp(self):
        super(ForeignKeyReprSuite, self).setUp()

        # What model is being tested?
        self._testing_model = Movie

        # Create the model instance.
        Movie.objects.create(
            title='The Hobbit',
            year_published=2012,
            based_on=Book.objects.get(title='The Hobbit'),
        )


class M2MReprSuite(BasicReprSuite):
    """A class for testing many to many repr prints.

    Since the many to many field is not technically part of
    Model._meta.fields, it is just skipped, and therefore this test does
    very little.

    It remains in place in case Django's behavior should change, as unlikely
    as that is.
    """
    def setUp(self):
        super(M2MReprSuite, self).setUp()

        # What model is being tested?
        self._testing_model = Publisher

        # Create thje model instances.
        Book.objects.create(
            title='The Fellowship of the Ring',
            year_published=1954,
        )
        publisher = Publisher.objects.create(
            name='Ballantine Books',
        )
        for book in Book.objects.all():
            publisher.books.add(book)


class RecursiveReprSuite(BasicReprSuite):
    """Test case for printing of recursive relationships, and establishing
    that we avoid any recursive traps.
    """
    def setUp(self):
        # What model is being tested?
        self._testing_model = Character

        # Create the model instances.
        gandalf = Character.objects.create(
            name='Gandalf',
        )
        sauron = Character.objects.create(
            name='Sauron',
            enemy=gandalf,
        )
        gandalf.enemy = sauron
        gandalf.save()

    @override_settings(DJANGOPG_REPR_TEMPLATE='single_line')
    def test_single_line_repr(self):
        instance = super(RecursiveReprSuite, self).test_single_line_repr()
        assert '**RECURSION**' in repr(instance)
        return instance

    @override_settings(DJANGOPG_REPR_TEMPLATE='multi_line')
    def test_multi_line_repr(self):
        instance = super(RecursiveReprSuite, self).test_multi_line_repr()
        assert '**RECURSION**' in repr(instance)
        return instance


class SupportSuite(TestCase):
    """Test case for odds and ends around improved repr functionality."""
    def setUp(self):
        Book.objects.create(
            title='The Hobbit',
            year_published=1937,
        )

    @override_settings(DJANGOPG_REPR_TEMPLATE=('Look, it is my book!', ''))
    def test_simple_custom_template(self):
        book = Book.objects.get()
        self.assertEqual(repr(book), 'Look, it is my book!')

    @override_settings(DJANGOPG_REPR_TEMPLATE=('{%(members)s}', ', '))
    def test_dict_template(self):
        book = Book.objects.get()
        expected_value = []
        for field in [i.name for i in Book._meta.fields]:
            expected_value.append('%r: %r' % (field, getattr(book, field)))
        expected_value = '{%s}' % ', '.join(expected_value)
        self.assertEqual(repr(book), expected_value)


class ExcludeSuite(TestCase):
    def setUp(self):
        Movie.objects.create(
            title='The Hobbit',
            year_published=2012,
        )
        Interview.objects.create(
            subject='Peter Jackson',
            role='Director',
            movie=Movie.objects.get(),
            on_dvd=False,
            on_blu_ray=True,
        )

    def test_interview_repr(self):
        interview = Interview.objects.get()
        assert re.search(r"u?'subject': u?'Peter Jackson'", repr(interview))
        assert re.search(r"u?'role': u?'Director", repr(interview))
        assert 'on_dvd' not in repr(interview)
        assert 'on_blu_ray' not in repr(interview)


class IncludeSuite(TestCase):
    def setUp(self):
        Studio.objects.create(
            name='Wingnut Films',
            net_worth=450 * (10 ** 6),
        )

    def test_studio_repr(self):
        studio = Studio.objects.get()
        assert re.search(r"u?'name': u?'Wingnut Films'", repr(studio))
        assert 'net_worth' not in repr(studio)
        assert '450000000' not in repr(studio)
