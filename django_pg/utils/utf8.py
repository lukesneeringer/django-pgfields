from __future__ import absolute_import, unicode_literals


class UnicodeAdapter(object):
    """Class for quoting a unicode string such that 4-bit unicode character
    support is retained.
    """
    def __init__(self, unicode_string):
        self._str = unicode_string

    def getquoted(self):
        """Return a bytes string, enclosed in single quotes, with single-quotes
        and backslashes duplicated.
        """
        s = self._str

        # Replace single-quote `'` with two consecutive single-quotes.
        s = s.replace("'", "''")

        # Replace backslash with two consecutive backslashes.
        # Note: I'd prefer the r'\' form, but I expect it won't play nice
        #   with some people's editors. Better to be safe.
        s = s.replace('\\', '\\\\')

        # Add the single-quotes on the sides, and return a utf8-encoded
        # bytes object.
        return ("'%s'" % s).encode('utf8')
