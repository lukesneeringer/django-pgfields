from distutils.core import setup
from os.path import dirname, realpath
from os import sep
from setuptools import find_packages
import pgfields

pip_requirements = dirname(realpath(__file__)) + sep + 'requirements.txt'

setup(
    name='django-pgfields',
    version=pgfields.VERSION,
    author='Luke Sneeringer',
    author_email='luke@sneeringer.com',

    description=' '.join((
        'Provides Field subclasses for PostgreSQL types,',
        'including arrays and composite types.',
    )),
    license='New BSD',

    install_requires=open(pip_requirements, 'r').read().strip().split('\n'),
    provides=[
        'pgfields',
    ],
    packages=find_packages(),
)