from __future__ import absolute_import, unicode_literals
from importlib import import_module
import os
import sys


# Get the project root directory, and add it to `sys.path`.
current_file = __file__
if __name__ == '__main__':
    current_file = '%s/%s' % (os.getcwd(), __file__)
sys.path.insert(0, os.path.realpath(os.path.dirname(current_file) + '/../'))

# Add the Django settings module to the environment.
if 'gis' in sys.argv:
    sys.argv.pop(sys.argv.index('gis'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings_gis'
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

# If we're in Django 1.7, we must explicitly set up the
# application registry.
import django
if hasattr(django, 'setup'):
    django.setup()

# Run tests.
from django.core.management import call_command

if __name__ == '__main__':
    args = sys.argv[1:]
    call_command('test', *args)
