from django.test import TestCase
from django.test.utils import override_settings
from django_pg import models
from django_pg.models.base import select_manager


class CustomManagerSuite(TestCase):
    """Test suite to establish that we get the right thing
    when establishing a custom manager in settings.py.

    The repitition in the individual tests is necessary;
    it's not possible to create a single model and re-use it because
    of funny business within Django itself.
    """
    @override_settings(DJANGOPG_DEFAULT_MANAGER='django_pg.models.Manager')
    def test_base_manager_str(self):
        class Foo1(models.Model):
            objects = select_manager()
            bar = models.IntegerField()
        self.assertIsInstance(Foo1.objects, models.Manager)

    @override_settings(DJANGOPG_DEFAULT_MANAGER=models.Manager)
    def test_base_manager_obj(self):
        class Foo2(models.Model):
            objects = select_manager()
            bar = models.IntegerField()
        self.assertIsInstance(Foo2.objects, models.Manager)

    @override_settings(DJANGOPG_DEFAULT_MANAGER='django_pg.models.GeoManager')
    def test_geo_manager_str(self):
        class Foo3(models.Model):
            objects = select_manager()
            bar = models.IntegerField()
        self.assertIsInstance(Foo3.objects, models.GeoManager)

    @override_settings(DJANGOPG_DEFAULT_MANAGER=models.GeoManager)
    def test_geo_manager_obj(self):
        class Foo4(models.Model):
            objects = select_manager()
            bar = models.IntegerField()
        self.assertIsInstance(Foo4.objects, models.GeoManager)
        

class ErrorSuite(TestCase):
    """Test suite for error cases involved in the default module setting."""

    @override_settings(DJANGOPG_DEFAULT_MANAGER='Manager')
    def test_bad_string(self):
        """Estblish that, if we provide a string that doesn't look
        like a Python module, that we raise ImportError.
        """
        with self.assertRaises(ImportError):
            class Foo(models.Model):
                objects = select_manager()
                bar = models.IntegerField()

    @override_settings(DJANGOPG_DEFAULT_MANAGER='bogus.Manager')
    def test_bad_module(self):
        """Estblish that, if we provide a string that doesn't look
        like a Python module, that we raise ImportError.
        """
        with self.assertRaises(ImportError):
            class Foo(models.Model):
                objects = select_manager()
                bar = models.IntegerField()
