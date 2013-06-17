from distutils.core import setup
from os.path import dirname, realpath
from os import sep
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import sys

pip_requirements = 'requirements.txt'
version = open('VERSION').read().strip()

class Tox(TestCommand):
    """The test command should install and then run tox.

    Bawed on http://tox.readthedocs.org/en/latest/example/basic.html
    """
    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # Import here, because outside eggs aren't loaded.
        sys.exit(tox.cmdline(self.test_args))


setup(
    # Basic metadata
    name='django-pgfields',
    version=version,
    author='Luke Sneeringer',
    author_email='luke@sneeringer.com',
    url='https://github.com/lukesneeringer/django-pgfields',

    # Additional information
    description=' '.join((
        'Provides custom Field subclasses intended for use with types',
        'available in PostgreSQL but not in the Django core ORM,',
        'including arrays and composite types.',
    )),
    license='New BSD',

    # How to do the install
    install_requires=open(pip_requirements, 'r').read().strip().split('\n'),
    provides=[
        'django_pg',
    ],
    packages=find_packages(),

    # How to do the tests
    tests_require=['tox'],
    cmdclass={'test': Tox },

    # PyPI metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Database',
        'Topic :: Software Development',
    ],
)
