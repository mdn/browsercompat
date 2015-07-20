# coding: utf-8
"""Parser for Specification section of an MDN raw page."""

from .html import HTMLElement, HTMLText
from .kumascript import KumaVisitor, SpecName, Spec2


class SpecNameVisitor(KumaVisitor):
    """
    Visitor for a SpecName HTML fragment.

    This is the first column of the Specifications table.
    """
    scope = 'specification name'

    def __init__(self, **kwargs):
        super(SpecNameVisitor, self).__init__(**kwargs)
        self.mdn_key = None
        self.subpath = None
        self.section_name = None
        self.spec_item = None
        self.spec = None

    def process(self, cls, node, **kwargs):
        """Look for SpecName nodes."""
        processed = super(SpecNameVisitor, self).process(
            cls, node, **kwargs)
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
        elif (isinstance(processed, HTMLText) and processed.cleaned):
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
                self.spec = self.data.specification_by_key(key)
                if not self.spec:
                    self.add_issue('unknown_spec', self.spec_item, key=key)
            else:
                self.add_issue(
                    'specname_not_kumascript', processed, original=text)
        return processed


class Spec2Visitor(KumaVisitor):
    """
    Visitor for a Spec2 HTML fragment.

    This is the second column of the Specifications table.
    """
    scope = 'specification maturity'

    def __init__(self, **kwargs):
        super(Spec2Visitor, self).__init__(**kwargs)
        self.mdn_key = None
        self.spec2_item = None
        self.spec = None
        self.maturity = None

    def process(self, cls, node, **kwargs):
        """Look for Spec2 nodes."""
        processed = super(Spec2Visitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, Spec2):
            assert not self.spec2_item
            assert not self.mdn_key
            self.spec2_item = processed
            self.mdn_key = processed.mdn_key
            self.spec = processed.spec
            if self.spec:
                self.maturity = self.spec.maturity
        elif isinstance(processed, SpecName):
            self.spec2_item = processed
            self.mdn_key = processed.mdn_key
            self.spec = processed.spec
            self.maturity = self.spec.maturity if self.spec else None
            self.add_raw_issue(processed._make_issue('spec2_wrong_kumascript'))
        elif (isinstance(processed, HTMLText) and processed.cleaned and
                not self.mdn_key and not self.spec2_item):
            self.spec2_item = processed
        return processed


class SpecDescVisitor(KumaVisitor):
    """
    Visitor for a Specification description fragment.

    This is the third column of the Specifications table.
    """
    scope = 'specification description'

    def __init__(self, **kwargs):
        super(SpecDescVisitor, self).__init__(**kwargs)
        self.desc_items = None

    def process(self, cls, node, **kwargs):
        """Look for description nodes."""
        processed = super(SpecDescVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLElement) and processed.tag == 'td':
            assert self.desc_items is None
            self.desc_items = processed.children
        return processed
