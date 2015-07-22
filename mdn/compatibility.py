# coding: utf-8
"""Parser for Compatibility section of an MDN raw page."""
from __future__ import unicode_literals
from collections import OrderedDict
import re

from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type
from parsimonious.grammar import Grammar

from .html import HTMLElement, HTMLText
from .kumascript import (
    CompatAndroid, CompatGeckoDesktop, CompatGeckoFxOS, CompatGeckoMobile,
    CompatNightly, CompatNo, CompatUnknown, CompatVersionUnknown,
    DeprecatedInline, ExperimentalInline, KumaScript, KumaVisitor,
    NonStandardInline, NotStandardInline, PropertyPrefix,
    kumascript_grammar_source)
from .utils import is_new_id, join_content

compat_shared_grammar_source = r"""
footnote_id = "[" ~r"(?P<content>\d+|\*+)" "]"
text_item = ~r"(?P<content>[^{<[]+)"s
"""

compat_feature_grammar_source = kumascript_grammar_source + r"""
#
# Add compat feature strings to text_token
#
text_token = kumascript / footnote_id / text_item
""" + compat_shared_grammar_source

compat_support_grammar_source = kumascript_grammar_source + (
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
""") + compat_shared_grammar_source

compat_feature_grammar = Grammar(compat_feature_grammar_source)
compat_support_grammar = Grammar(compat_support_grammar_source)
compat_footnote_grammar = compat_feature_grammar


@python_2_unicode_compatible
class Footnote(HTMLText):
    """A Footnote, like [1]."""

    def __init__(self, footnote_id, **kwargs):
        super(Footnote, self).__init__(**kwargs)
        self.raw_footnote = footnote_id.strip()
        if self.raw_footnote.isnumeric():
            self.footnote_id = self.raw_footnote
        else:
            # TODO: use raw footnote instead
            self.footnote_id = text_type(len(self.raw_footnote))

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
    scope = 'compatibility feature'

    def __init__(self, parent_feature, *args, **kwargs):
        """Initialize a CompatFeatureVisitor.

        Keyword Arguments:
        parent_feature - The parent feature
        """
        super(CompatFeatureVisitor, self).__init__(*args, **kwargs)
        self.parent_feature = parent_feature
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
        if isinstance(processed, HTMLElement) and processed.tag == 'td':
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
        elif isinstance(element, (HTMLText, HTMLElement)):
            return element.to_html()

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
        feature_params = self.data.lookup_feature_params(
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

    visit_a_open = KumaVisitor._visit_drop_tag_open
    visit_p_open = KumaVisitor._visit_drop_tag_open
    visit_strong_open = KumaVisitor._visit_drop_tag_open
    visit_sup_open = KumaVisitor._visit_drop_tag_open

    visit_a_element = KumaVisitor._visit_drop_tag_element
    visit_p_element = KumaVisitor._visit_drop_tag_element
    visit_strong_element = KumaVisitor._visit_drop_tag_element
    visit_sup_element = KumaVisitor._visit_drop_tag_element


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


class CellRemoved(HTMLText):
    """The prefix text "Removed in"."""


class CellNoPrefix(HTMLText):
    """The suffix text (unprefixed) or (no prefix)."""


class CellPartial(HTMLText):
    """The suffix text (partial)."""


class CompatSupportVisitor(CompatBaseVisitor):
    scope = 'compatibility support'

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
        self.versions = []
        self.supports = []
        self.inline_texts = []
        self.init_version_and_support()

    def init_version_and_support(self):
        self.version = {'browser': self.browser_id}
        self.support = {'feature': self.feature_id}

    def commit_support_and_version(self):
        """Commit new or updated support and version, and prepare for next."""
        if self.version.get('version'):
            if (self.support.get('support') == 'yes' and
                    self.support.get('prefix') and
                    self.support.get('footnote_id')):
                # Footnote + prefix => support=partial
                self.support['support'] = 'partial'
            self.versions.append(self.version)
            self.supports.append(self.support)
            self.init_version_and_support()

    def add_inline_text_issues(self):
        """Add the 'widest' inline text issues."""
        # Sort by start and end positions of inline text
        spans = []
        for node, text in self.inline_texts:
            spans.append((node.start, node.end, node, text))
        spans.sort()

        # Add issues for non-empty text that hasn't already been added
        last_position = -1
        for start, end, node, text in spans:
            if text and start >= last_position:
                self.add_issue('inline_text', node, text=text)
                last_position = node.end

    def process(self, cls, node, **kwargs):
        processed = super(CompatSupportVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLElement):
            tag = processed.tag
            if tag == 'td':
                self.add_inline_text_issues()
                self.commit_support_and_version()
            elif tag == 'code':
                self.inline_texts.append((processed, processed.to_html()))
        elif isinstance(processed, CellVersion):
            self.set_version(processed.version, processed)
        elif isinstance(processed, CompatVersionUnknown):
            self.set_version('current', processed)
        elif isinstance(processed, CompatNightly):
            self.set_version('nightly', processed)
        elif isinstance(processed, CompatNo):
            self.set_version('current', processed)
            self.support['support'] = 'no'
        elif isinstance(processed, CompatUnknown):
            pass  # Don't record unknown support in API
        elif isinstance(processed, (
                CompatGeckoDesktop, CompatGeckoMobile, CompatAndroid)):
            version_name = str(processed.version)
            if self.is_valid_version(version_name):
                self.set_version(version_name, processed)
        elif isinstance(processed, CompatGeckoFxOS):
            if not (processed.bad_version or processed.bad_override):
                self.set_version(str(processed.version), processed)
        elif isinstance(processed, PropertyPrefix):
            self.support['prefix'] = processed.prefix
        elif isinstance(processed, Footnote):
            if self.support.get('footnote_id'):
                self.add_issue(
                    'footnote_multiple', processed,
                    prev_footnote_id=self.support['footnote_id'][0],
                    footnote_id=processed.footnote_id)
            else:
                self.support['footnote_id'] = (
                    processed.footnote_id, processed.start, processed.end)
        elif isinstance(processed, CellRemoved):
            self.commit_support_and_version()
            self.support['support'] = 'no'
        elif isinstance(processed, CellPartial):
            self.support['support'] = 'partial'
        elif isinstance(processed, CellNoPrefix):
            self.support['support'] = 'yes'
        elif isinstance(processed, KumaScript):
            if processed.known:
                self.add_raw_issue(processed._make_issue('unknown_kumascript'))
        elif isinstance(processed, HTMLText):
            self.inline_texts.append((processed, processed.cleaned))
        return processed

    version_re = re.compile(r"((\d+(\.\d+)*)|current|nightly)$")

    def is_valid_version(self, version_name):
        return bool(self.version_re.match(version_name))

    def set_version(self, version_name, element):
        """Set the version number, and determine if it is new or existing."""
        assert self.is_valid_version(version_name), 'Invalid version name'
        if self.version.get('version'):
            self.commit_support_and_version()
        version, version_id = self.data.lookup_version_params(
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

        support_id = self.data.lookup_support_id(
            version_id, self.feature_id)
        self.support['id'] = support_id
        self.support.setdefault('support', 'yes')
        self.support['version'] = version_id

    def visit_cell_version(self, node, children):
        version = node.match.group('version')
        engine_version = node.match.group('eng_version')
        return self.process(
            CellVersion, node, version=version, engine_version=engine_version)

    def visit_cell_removed(self, node, children):
        return self.process(CellRemoved, node)

    def visit_cell_noprefix(self, node, children):
        return self.process(CellNoPrefix, node)

    def visit_cell_partial(self, node, children):
        return self.process(CellPartial, node)


class CompatFootnoteVisitor(CompatBaseVisitor):
    scope = 'footnote'

    def __init__(self, *args, **kwargs):
        super(CompatFootnoteVisitor, self).__init__(*args, **kwargs)
        self._footnote_data = OrderedDict()
        self._current_footnote_id = None
        self.scope = 'footnote'

    def finalize_footnotes(self):
        """Finalize and return footnotes."""
        output = OrderedDict()
        for footnote_id, sections in self._footnote_data.items():
            lines = []
            start = None
            end = None
            for element, single, items in sections:
                open_tag = str(element.open_tag)
                close_tag = str(element.close_tag)
                if element.tag == 'pre':
                    content = join_content(item.raw for item in items)
                else:
                    content = join_content(item.to_html() for item in items)
                lines.append((open_tag, content, close_tag))
                if single:
                    start_element = element
                    end_element = element
                else:
                    start_element = items[0]
                    end_element = items[-1]
                if start is None:
                    start = start_element.start
                    end = end_element.end
                else:
                    start = min(start_element.start, start)
                    end = max(end_element.end, end)
            if len(lines) == 1:
                output[footnote_id] = (lines[0][1], start, end)
            else:
                output[footnote_id] = (
                    '\n'.join(''.join(line) for line in lines), start, end)
        return output

    def gather_content(self, element):
        """Gather footnote IDs and content from a container element."""
        footnote_id = self._current_footnote_id
        footnotes = OrderedDict(((footnote_id, []),))

        # Gather content by footnote ID
        for child in element.children:
            if isinstance(child, Footnote):
                footnote_id = child.footnote_id
                assert footnote_id not in footnotes
                footnotes[footnote_id] = []
            elif isinstance(child, (HTMLElement, HTMLText)):
                if child.to_html():
                    footnotes[footnote_id].append(child)

        # Store content for later combining
        self._current_footnote_id = footnote_id
        single = len([True for content in footnotes.values() if content]) == 1
        for footnote_id, content in footnotes.items():
            if content:
                if footnote_id is None:
                    if single:
                        self.add_issue('footnote_no_id', element)
                    else:
                        start = content[0].start
                        end = content[-1].end
                        self.add_raw_issue(('footnote_no_id', start, end, {}))
                else:
                    self._footnote_data.setdefault(footnote_id, []).append(
                        (element, single, content))

    def process(self, cls, node, **kwargs):
        processed = super(CompatFootnoteVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLElement):
            if processed.tag == 'p':
                self.gather_content(processed)
            elif processed.tag == 'pre':
                self._footnote_data[self._current_footnote_id].append(
                    (processed, True, processed.children))
        return processed
