# coding: utf-8
"""Parser for Compatibility section of an MDN raw page."""
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible

from .html import HTMLText, HTMLStructure
from .kumascript import (
    kumascript_grammar, DeprecatedInline, ExperimentalInline,
    NonStandardInline, NotStandardInline, KumaVisitor)
from .utils import is_new_id, join_content

compat_shared_grammar = r"""
footnote_id = "[" ~r"(?P<content>\d+|\*+)" "]"
text_item = ~r"(?P<content>[^{<[]+)"s
"""

compat_feature_grammar = kumascript_grammar + r"""
#
# Add compat feature strings to text_token
#
text_token = kumascript / footnote_id / text_item
""" + compat_shared_grammar

compat_support_grammar = kumascript_grammar + (
    r"""
#
# Add compat support strings to text_token
#
text_token = kumascript / cell_version / footnote_id / cell_removed /
    cell_noprefix / cell_partial / text_item
cell_version = ~r"(?P<version>\d+(\.\d+)*)"""
    r"""(\s+\((?P<eng_version>\d+(\.\d+)*)\))?\s*"s
cell_removed = ~r"[Rr]emoved\s+[Ii]n\s*"s
cell_noprefix = _ ("(unprefixed)" / "(no prefix)" / "without prefix" /
    "(without prefix)") _
cell_partial =  _ (", partial" / "(partial)") _
""") + compat_shared_grammar


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

    def to_feature_dict(self):
        """Convert to a dictionary of feature parameters, as used by parser."""
        feature = {
            'id': self.feature_id,
            'slug': self.slug,
            'name': self.name}
        if self.canonical:
            feature['canonical'] = True
        if self.experimental:
            feature['experimental'] = True
        if self.obsolete:
            feature['obsolete'] = True
        if not self.standardized:
            feature['standardized'] = False
        return feature


@python_2_unicode_compatible
class CellVersion(HTMLText):
    """A version string, like '1.0', '1', or '1.0 (85.0)'"""

    def __init__(self, version, engine_version=None, **kwargs):
        super(CellVersion, self).__init__(**kwargs)
        if '.' in version:
            self.version = version
        else:
            assert version
            assert int(version)
            self.version = version + '.0'
        self.engine_version = engine_version or None

    def __str__(self):
        if self.engine_version is None:
            return self.version
        else:
            return "{} ({})".format(self.version, self.engine_version)


class CompatSupportVisitor(CompatBaseVisitor):
    def __init__(
            self, feature_id, browser_id, browser_name, browser_slug=None,
            *args, **kwargs):
        """Initialize a CompatSupportVisitor.

        Keyword Arguments:
        feature_id - The feature ID for this row
        browser_id - The browser ID for this column
        browser_name - The browser name for this column
        browser_slug - The browser slug for this column
        """
        super(CompatSupportVisitor, self).__init__(*args, **kwargs)
        self.feature_id = feature_id
        self.browser_id = browser_id
        self.browser_name = browser_name
        self.browser_slug = browser_slug or '<no slug>'
        self.scope = 'compatibility support'
        self.versions = []
        self.supports = []
        self.init_version_and_support()

    def init_version_and_support(self):
        self.version = {'browser': self.browser_id}
        self.support = {'feature': self.feature_id}

    def commit_support_and_version(self, td):
        """Commit new or updated support and version, and prepare for next."""
        self.versions.append(self.version)
        self.supports.append(self.support)
        self.init_version_and_support()

    def process(self, cls, node, **kwargs):
        processed = super(CompatSupportVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLStructure) and processed.tag == 'td':
            self.commit_support_and_version(processed)
        elif isinstance(processed, CellVersion):
            self.set_version(processed.version, processed)
        return processed

    def set_version(self, version_name, element):
        """Set the version number, and determine if it is new or existing."""
        version, version_id = self.data.version_params_by_version(
            self.browser_id, self.browser_name, version_name)
        new_version = is_new_id(version_id)
        new_browser = is_new_id(self.browser_id)
        if new_version and not new_browser:
            self.add_issue(
                'unknown_version', element, browser_id=self.browser_id,
                browser_name=self.browser_name, version=version_name,
                browser_slug=self.browser_slug)
        self.version['id'] = version_id
        self.version['version'] = version_name

        support_id = self.data.support_id_by_relations(
            version_id, self.feature_id)
        self.support['id'] = support_id
        self.support.setdefault('support', 'yes')
        self.support['version'] = version_id

    def visit_cell_version(self, node, children):
        version = node.match.group('version')
        engine_version = node.match.group('eng_version')
        return self.process(
            CellVersion, node, version=version, engine_version=engine_version)
