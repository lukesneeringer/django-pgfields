from .settings import *


# Database settings. This assumes that the default user and empty
# password will work.
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_pg',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}


# Add `django.contrib.gis` to INSTALLED_APPS, so that the test
# database is created with GIS support.
INSTALLED_APPS.insert(0, 'django.contrib.gis')
