from copy import copy
from django_pg.utils.datatypes import CoerciveList
import unittest


class CoerciveListTestCase(unittest.TestCase):
    """Test case for coercive lists."""

    def test_insert(self):
        l = CoerciveList(lambda i: int(i), ['1', '2', 3, '5'])
        l.insert(1, '1')
        self.assertEqual(l, [1, 1, 2, 3, 5])
        self.assertEqual(l[0], 1)
        self.assertEqual(l[1], 1)
        self.assertEqual(l[2], 2)
        self.assertEqual(l[3], 3)
        self.assertEqual(l[4], 5)

    def test_repr(self):
        l = CoerciveList(lambda i: int(i), ['1', '1', '2', '3', '5'])
        self.assertEqual(repr(l), repr(list(l)))

    def test_copy(self):
        l = CoerciveList(lambda i: int(i), ['1', '1', '2', '3', '5'])
        self.assertEqual(l, [1, 1, 2, 3, 5])
        self.assertEqual(copy(l), [1, 1, 2, 3, 5])
        self.assertNotEqual(id(l), id(copy(l)))

    def test_append(self):
        l = CoerciveList(lambda i: int(i), ['1', '1', '2'])
        l.append('3')
        l.append(5.0)
        self.assertEqual(l, [1, 1, 2, 3, 5])

    def test_extend(self):
        l = CoerciveList(lambda i: int(i), ['1', '1'])
        l.extend(['2', 3, '5'])
        self.assertEqual(l, [1, 1, 2, 3, 5])
