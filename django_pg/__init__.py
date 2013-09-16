from __future__ import absolute_import, unicode_literals
import os


_dirname = os.path.dirname(os.path.realpath(__file__))
with open('%s/VERSION' % _dirname) as version_file:
    __version__ = tuple(
        version_file.read().strip().replace('-', '.').split('.'),
    )
