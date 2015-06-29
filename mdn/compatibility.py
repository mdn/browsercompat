# coding: utf-8
"""Parser for Compatibility section of an MDN raw page."""
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible

from .html import HTMLText, HTMLStructure
from .kumascript import (
    kumascript_grammar, DeprecatedInline, ExperimentalInline,
    NonStandardInline, NotStandardInline, KumaVisitor)
from .utils import join_content


compat_feature_grammar = kumascript_grammar + r"""
#
# Add compat feature strings to text_token
#
text_token = kumascript / footnote_id / text_item
footnote_id = "[" ~r"(?P<content>\d+|\*+)" "]"
text_item = ~r"(?P<content>[^{<[]+)"s
"""


@python_2_unicode_compatible
class Footnote(HTMLText):
    """A Footnote, like [1]."""

    def __init__(self, footnote_id, **kwargs):
        super(Footnote, self).__init__(**kwargs)
        self.footnote_id = footnote_id.strip()

    def __str__(self):
        return "[{}]".format(self.footnote_id)


class CompatBaseVisitor(KumaVisitor):
    """Shared visitor for compatibility content."""

    def visit_footnote_id(self, node, children):
        open_bracket, content, close_bracket = children
        return self.process(Footnote, node, footnote_id=content.text)


class CompatFeatureVisitor(CompatBaseVisitor):
    """
    Visitor for a compatibility feature cell

    This is the first column of the compatibilty table.
    """

    def __init__(self, parent_feature, *args, **kwargs):
        """Initialize a CompatFeatureVisitor.

        Keyword Arguments:
        parent_feature - The parent feature
        """
        super(CompatFeatureVisitor, self).__init__(*args, **kwargs)
        self.parent_feature = parent_feature
        self.scope = 'compatibility feature'
        self.name = None
        self.name_bits = []
        self.feature_id = None
        self.canonical = False
        self.experimental = False
        self.standardized = True
        self.obsolete = False
        self.feature = None

    def process(self, cls, node, **kwargs):
        processed = super(CompatFeatureVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLStructure) and processed.tag == 'td':
            self.finalize_feature(processed)
        elif isinstance(processed, Footnote):
            self.add_issue('footnote_feature', processed)
        elif isinstance(processed, DeprecatedInline):
            self.obsolete = True
        elif isinstance(processed, ExperimentalInline):
            self.experimental = True
        elif isinstance(processed, (NonStandardInline, NotStandardInline)):
            self.standardized = False
        return processed

    def gather_text(self, element):
        if isinstance(element, Footnote):
            return ''
        elif isinstance(element, HTMLText):
            return element.to_html()
        elif isinstance(element, HTMLStructure):
            tag = element.tag
            if tag == 'code':
                return element.to_html()
            else:
                self.add_issue(
                    'tag_dropped', element, tag=tag, scope=self.scope)
                sub_text = [self.gather_text(ch) for ch in element.children]
                return join_content(sub_text)

    def finalize_feature(self, td):
        """Finalize a new or updated feature."""
        # Gather text
        for child in td.children:
            self.name_bits.append(self.gather_text(child))
        assert self.name_bits

        # Construct the name
        assert self.name is None
        name = join_content(self.name_bits)
        if (name.startswith('<code>') and name.endswith('</code>') and
                name.count('<code>') == 1):
            self.canonical = True
            name = name[len('<code>'):-len('</code>')]
        self.name = name

        # Construct or lookup ID and slug
        feature_params = self.data.feature_params_by_name(
            self.parent_feature, self.name)
        self.feature, self.feature_id, self.slug = feature_params
