# coding: utf-8
"""Parser for SpecName section of MDN raw page."""

from .html import HTMLText
from .kumascript import KumaVisitor, SpecName

from webplatformcompat.models import Specification


class SpecNameVisitor(KumaVisitor):
    """
    Visitor for a SpecName HTML fragment.

    This is the first column of the Specifications table.
    """
    def __init__(self, *args, **kwargs):
        super(SpecNameVisitor, self).__init__(*args, **kwargs)
        self.scope = 'specification name'
        self.mdn_key = None
        self.subpath = None
        self.section_name = None
        self.spec_item = None
        self.spec = None
        self.issues = []

    def process(self, cls, node, *args, **kwargs):
        """Look for SpecName nodes."""
        processed = super(SpecNameVisitor, self).process(
            cls, node, *args, **kwargs)
        if isinstance(processed, SpecName):
            assert not self.spec_item
            assert not self.mdn_key
            assert not self.subpath
            assert not self.section_name
            self.spec_item = processed
            self.mdn_key = processed.mdn_key
            self.subpath = processed.subpath
            self.section_name = processed.section_name
            self.spec = processed.spec
        elif isinstance(processed, HTMLText) and processed.cleaned:
            text = processed.cleaned
            legacy_specs = {
                'ECMAScript 1st Edition.': 'ES1',
                'ECMAScript 3rd Edition.': 'ES3'}
            key = legacy_specs.get(text, '')
            if key:
                self.mdn_key = key
                self.spec_item = processed
                self.add_issue(
                    'specname_converted', processed, original=text, key=key)
                try:
                    self.spec = Specification.objects.get(mdn_key=key)
                except Specification.DoesNotExist:
                    self.add_issue('unknown_spec', self.spec_item, key=key)
            else:
                self.add_issue(
                    'specname_not_kumascript', processed, original=text)
        return processed
