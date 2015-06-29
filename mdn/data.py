# coding: utf-8
"""Data lookup operations for MDN parsing."""

from webplatformcompat.models import Specification


class Data(object):
    """
    Provide data operations for MDN parsing.

    Parsing an MDN page requires loading existing data for many purposes.
    This class loads the data and, if it can, caches the data.
    """

    def __init__(self):
        self.specifications = {}

    def specification_by_key(self, mdn_key):
        """Retrieve a Specification by key."""
        if mdn_key not in self.specifications:
            try:
                spec = Specification.objects.get(mdn_key=mdn_key)
            except Specification.DoesNotExist:
                spec = None
            self.specifications[mdn_key] = spec
        return self.specifications[mdn_key]
