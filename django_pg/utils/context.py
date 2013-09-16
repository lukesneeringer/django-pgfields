from __future__ import absolute_import, unicode_literals
import contextlib
import io
import sys


@contextlib.contextmanager
def redirect_std():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        std = {
            'out': io.StringIO(),
            'err': io.StringIO(),
        }
        sys.stdout, sys.stderr = std['out'], std['err']
        yield std

    finally:
        sys.stdout, sys.stderr = oldout, olderr
