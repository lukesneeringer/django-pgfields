from __future__ import unicode_literals
import os


_dirname = os.path.dirname(os.path.realpath(__file__))
__version__ = tuple(
    open('%s/VERSION' % _dirname).read().strip().replace('-', '.').split('.'),
)
