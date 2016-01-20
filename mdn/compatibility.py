# coding: utf-8
"""Parser for Compatibility section of an MDN raw page."""
from __future__ import unicode_literals
from collections import OrderedDict
import re

from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type
from parsimonious.grammar import Grammar

from .html import HnElement, HTMLElement, HTMLText
from .kumascript import (
    CompatGeckoFxOS, CompatKumaScript, CompatNightly, CompatNo, CompatUnknown,
    CompatVersionUnknown, DeprecatedInline, EmbedCompatTable,
    ExperimentalInline, KumaScript, KumaVisitor, NonStandardInline,
    NotStandardInline, ObsoleteInline, PropertyPrefix,
    kumascript_grammar_source)
from .utils import is_new_id, format_version, join_content
from .visitor import Extractor

compat_shared_grammar_source = r"""
footnote_id = _ "[" ~r"(?P<content>\d+|\*+)" "]" _
bracket_text = _ ~r"(?P<content>\[[^]]+\])" _
text_item = ~r"(?P<content>[^{<[]+)"s
"""

compat_feature_grammar_source = kumascript_grammar_source + r"""
#
# Add compat feature strings to text_token
#
text_token = kumascript / footnote_id / bracket_text / text_item
""" + compat_shared_grammar_source

compat_support_grammar_source = kumascript_grammar_source + (
    r"""
#
# Add compat support strings to text_token
#
text_token = kumascript / cell_version / footnote_id / bracket_text /
    cell_removed / cell_noprefix / cell_partial / text_item
cell_version = _ ~r"(?P<version>\d+(\.\d+)*)"""
    r"""(\s+\((?P<eng_version>\d+(\.\d+)*)\))?\s*"s _
cell_removed = _ ~r"[Rr]emoved\s+[Ii]n\s*"s _
cell_noprefix = _ ("(unprefixed)" / "(no prefix)" / "without prefix" /
    "(without prefix)") _
cell_partial =  _ (", partial" / "(partial)") _
""") + compat_shared_grammar_source

compat_feature_grammar = Grammar(compat_feature_grammar_source)
compat_support_grammar = Grammar(compat_support_grammar_source)
compat_footnote_grammar = compat_feature_grammar


class CompatSectionExtractor(Extractor):
    """Extracts data from elements parsed from a Browser Compatibility section.

    A Browser Compatibility section looks like this:

    <h2 id="Browser_compatibility">Browser compatibility</h2>
    <div>{{CompatibilityTable}}</div>
    <div id="compat-desktop">
      <table class="compat-table">
        <tbody>
          <tr><th>Feature</th><th>Chrome</th></tr>
          <tr><td>Basic support</td><td>1.0 [1]</td></tr>
          <tr><td><code>contain</code></td><td>3.0</td></tr>
        </tbody>
      </table>
    </div>
    <p>[1] This is a footnote.</p>
    """

    extractor_name = 'Compatibility Extractor'

    def __init__(self, feature, **kwargs):
        self.feature = feature
        self.initialize_extractor(**kwargs)

    def setup_extract(self):
        self.compat_divs = []
        self.footnote_elems = []
        self.footnotes = OrderedDict()
        self.embedded = []
        self.reset_compat_div()

    def reset_compat_div(self):
        self.browsers = OrderedDict()
        self.columns = []
        self.compat_div = None
        self.rows = []
        self.row = []

    def entering_element(self, state, element):
        """Extract and change state when entering an element.

        Return is a tuple:
        - The next state
        - True if the child elements should be walked, False if already
          processed or can be skipped.
        """
        if state == 'begin':
            assert isinstance(element, HnElement)
            # TODO: Check id and name
            return 'before_compat_div', False
        elif state == 'before_compat_div':
            if self.is_tag(element, 'p') or self.is_tag(element, 'div'):
                is_compat_div = self.extract_pre_compat_element(element)
                if is_compat_div:
                    return 'compat_div', True
                else:
                    return 'before_compat_div', False
        elif state == 'compat_div':
            if self.is_tag(element, 'table'):
                return 'in_table', True
        elif state == 'in_table':
            if self.is_tag(element, 'tr'):
                return 'in_header_row', True
        elif state == 'in_header_row':
            if self.is_tag(element, 'th'):
                self.extract_feature_header(element)
                return 'in_browser_names', False
        elif state == 'in_browser_names':
            # Transition to 'extracted_row' happens on </tr>
            if self.is_tag(element, 'th'):
                self.extract_browser_name(element)
                return 'in_browser_names', False
        elif state == 'extracted_row':
            # Transition to 'after_compat_div' happens on </table>
            if self.is_tag(element, 'tr'):
                return 'in_data_row', True
        elif state == 'in_data_row':
            # Transition to "extracted_row" happens on </tr>
            if self.is_tag(element, 'td'):
                self.extract_cell(element)
                return 'in_data_row', False
        elif state == 'after_compat_div':
            if self.is_tag(element, 'p') or self.is_tag(element, 'div'):
                next_state, descend = self.extract_post_compat_div(element)
                assert next_state in (
                    'after_compat_div', 'compat_div', 'in_footnotes')
                return next_state, descend
        elif state == 'in_footnotes':
            self.extract_footnotes(element)
            return 'in_footnotes', False
        else:  # pragma: no cover
            raise Exception('Unexpected state "{}"'.format(state))
        return state, True

    def leaving_element(self, state, element):
        """Process data and change state when exiting an element.

        Return is the next state.
        """
        if state == 'begin':  # pragma: no cover
            pass
        elif state == 'before_compat_div':
            pass
        elif state == 'compat_div':
            pass
        elif state == 'in_table':
            pass
        elif state == 'in_header_row':  # pragma: no cover
            pass
        elif state == 'in_browser_names':
            if self.is_tag(element, 'tr'):
                return 'extracted_row'
        elif state == 'extracted_row':
            if self.is_tag(element, 'table'):
                self.process_table()
                return 'after_compat_div'
        elif state == 'in_data_row':
            if self.is_tag(element, 'tr'):
                self.process_row()
                return 'extracted_row'
        elif state == 'after_compat_div':
            pass
        elif state == 'in_footnotes':
            pass
        else:  # pragma: no cover
            raise Exception('Unexpected state "{}"'.format(state))
        return state

    def extracted_data(self):
        self.process_footnotes()
        return {
            'compat_divs': self.compat_divs,
            'footnotes': self.footnotes,
            'issues': self.issues,
            'embedded': self.embedded,
        }

    def extract_pre_compat_element(self, element):
        """Parse <p> and <div> elements before a table.

        Looking for:
        <div id="compat-section"> - Start parsing
        <p>{{CompatibilityTable}}</p> - Ignore
        <p>{{EmbedCompatTable("slug")}}</p> - Extract slug
        Others - If has content, issue warning
        """
        # Is it a compatibility div?
        div_name = self.is_compat_div(element)
        if div_name is not None:
            self.compat_div = {'name': div_name}
            return True

        # Look for {{EmbedCompatTable("slug")}} macros
        self.embedded.extend(self.extract_embedcompattable_div(element))

        # Is there visible content?
        if element.to_html(drop_tag=True):
            self.add_issue('skipped_content', element)
        return False

    def is_compat_div(self, element):
        """Return the name if a compat div, or None."""
        if self.is_tag(element, 'div'):
            div_id = element.attributes.get('id', '')
            if div_id.startswith('compat-'):
                _, name = div_id.split('-', 1)
                return name

    def extract_embedcompattable_div(self, element):
        """Extract slugs from {{EmbedCompatTable}} macros."""
        slugs = []
        for child in element.children:
            if isinstance(child, EmbedCompatTable):
                slugs.append(child.arg(0))
            elif hasattr(child, 'children'):
                slugs.extend(self.extract_embedcompattable_div(child))
        return slugs

    def extract_feature_header(self, element):
        header = element.to_text()
        if header != 'Feature':
            self.add_issue('feature_header', element, header=header)
        self.columns.append(header)

    def extract_browser_name(self, element):
        colspan = int(element.attributes.get('colspan', 1))
        raw_name = element.to_text()
        browser_params = self.data.lookup_browser_params(raw_name)
        browser, browser_id, name, slug = browser_params
        if not browser:
            self.add_issue('unknown_browser', element, name=raw_name)
        self.browsers[browser_id] = {
            'id': browser_id, 'name': name, 'slug': slug}
        self.columns.extend([browser_id] * colspan)

    def extract_cell(self, element):
        self.row.append(element)

    def process_row(self):
        self.rows.append(self.row)
        self.row = []

    def process_table(self):
        """Process the collected table into features and supports."""
        features = OrderedDict()
        versions = OrderedDict()
        supports = OrderedDict()

        # Create an empty row grid
        table = []
        for row in range(len(self.rows)):
            table_row = []
            for col in range(len(self.columns)):
                table_row.append(None)
            table.append(table_row)

        # Parse the rows for features and supports
        for row, compat_row in enumerate(self.rows):
            for cell in compat_row:
                assert cell.tag == 'td'
                try:
                    col = table[row].index(None)
                except ValueError:
                    self.add_issue('extra_cell', cell)
                    continue
                rowspan = int(cell.attributes.get('rowspan', 1))
                colspan = int(cell.attributes.get('colspan', 1))
                if col == 0:
                    # Insert as feature
                    feature = self.cell_to_feature(cell)
                    cell_id = feature['id']
                    features[feature['id']] = feature
                else:
                    # Insert as support
                    feature_id = table[row][0]
                    assert feature_id
                    feature = features[feature_id]
                    browser_id = self.columns[col]
                    browser = self.browsers[browser_id]
                    cell_versions, cell_supports = self.cell_to_support(
                        cell, feature, browser)
                    cell_id = []
                    for version in cell_versions:
                        versions[version['id']] = version
                    for support in cell_supports:
                        cell_id.append(support['id'])
                        supports[support['id']] = support
                # Insert IDs into table
                for r in range(rowspan):
                    for c in range(colspan):
                        try:
                            table[row + r][col + c] = cell_id
                        except IndexError:
                            self.add_issue('cell_out_of_bounds', cell)

        # Commit scraped data
        self.compat_div['browsers'] = list(self.browsers.values())
        self.compat_div['versions'] = list(versions.values())
        self.compat_div['features'] = list(features.values())
        self.compat_div['supports'] = list(supports.values())
        self.compat_divs.append(self.compat_div)
        self.reset_compat_div()

    def cell_to_feature(self, cell):
        """Parse cell items as a feature (first column)."""
        raw_text = cell.raw
        reparsed = compat_feature_grammar.parse(raw_text)
        visitor = CompatFeatureVisitor(
            parent_feature=self.feature, offset=cell.start, data=self.data)
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.add_raw_issue(issue)
        feature = visitor.to_feature_dict()
        return feature

    def cell_to_support(self, cell, feature, browser):
        """Parse a cell as a support (middle cell)."""
        raw_text = cell.raw
        reparsed = compat_support_grammar.parse(raw_text)
        visitor = CompatSupportVisitor(
            feature_id=feature['id'], browser_id=browser['id'],
            browser_name=browser['name'], browser_slug=browser['slug'],
            offset=cell.start, data=self.data)
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.add_raw_issue(issue)
        return visitor.versions, visitor.supports

    def extract_post_compat_div(self, element):
        # Is it a compatibility div?
        div_name = self.is_compat_div(element)
        if div_name is not None:
            self.compat_div = {'name': div_name}
            return 'compat_div', True

        # Is there visible content?
        if element.to_html(drop_tag=True):
            self.extract_footnotes(element)
            return 'in_footnotes', False

        # Is there an EmbedCompatTable() macro?
        self.embedded.extend(self.extract_embedcompattable_div(element))

        # Keep looking for compatibility div or footnotes
        return 'after_compat_div', False

    def extract_footnotes(self, element):
        self.footnote_elems.append(element)

    def process_footnotes(self):
        if self.footnote_elems:
            # Reassemble raw HTML from elements
            start = self.footnote_elems[0].start
            last = start
            raw_bits = []
            for elem in self.footnote_elems:
                if elem.start != last:
                    self.add_raw_issue((
                        'footnote_gap', last + 1, elem.start - 1, {}))
                raw_bits.append(elem.raw)
                last = elem.end

            # Reparse as footnotes
            raw_text = ''.join(raw_bits)
            reparsed = compat_footnote_grammar.parse(raw_text)
            visitor = CompatFootnoteVisitor(offset=start)
            visitor.visit(reparsed)
            footnotes = visitor.finalize_footnotes()
            for issue in visitor.issues:
                self.add_raw_issue(issue)
            self.embedded.extend(visitor.embedded)
        else:
            footnotes = {}

        # Merge footnotes into supports
        used_footnotes = set()
        for div in self.compat_divs:
            for support in div['supports']:
                if 'footnote_id' in support:
                    f_id, f_start, f_end = support['footnote_id']
                    try:
                        text, start, end = footnotes[f_id]
                    except KeyError:
                        self.add_raw_issue((
                            'footnote_missing', f_start, f_end,
                            {'footnote_id': f_id}))
                    else:
                        support['footnote'] = text
                        used_footnotes.add(f_id)

        # Report and save unused footnotes
        for f_id in used_footnotes:
            del footnotes[f_id]

        for f_id, (text, start, end) in footnotes.items():
            self.add_raw_issue((
                'footnote_unused', start, end, {'footnote_id': f_id}))

        self.footnotes = footnotes


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

    def to_html(self):
        return ''

    def __str__(self):
        return '[{}]'.format(self.footnote_id)


class CompatBaseVisitor(KumaVisitor):
    """Shared visitor for compatibility cell and footnote content."""

    def visit_footnote_id(self, node, children):
        ws1, open_bracket, content, close_bracket, ws2 = children
        return self.process(Footnote, node, footnote_id=content.text)

    def visit_bracket_text(self, node, children):
        ws1, content, ws2 = children
        return self.process(HTMLText, content)

    def visit_td_open(self, node, children):
        """Retain colspan and rowspan attributes of <td> tags."""
        actions = {None: 'ban', 'colspan': 'keep', 'rowspan': 'keep'}
        return self._visit_open(node, children, actions)


class CompatFeatureVisitor(CompatBaseVisitor):
    """
    Visitor for a compatibility feature cell.

    This is the first column of the compatibility table.
    """

    scope = 'compatibility feature'
    _allowed_tags = ['code', 'td', 'br']

    def __init__(self, parent_feature, **kwargs):
        """Initialize a CompatFeatureVisitor.

        Keyword Arguments:
        parent_feature - The parent feature
        """
        super(CompatFeatureVisitor, self).__init__(**kwargs)
        self.parent_feature = parent_feature
        self.name = None
        self.feature_id = None
        self.canonical = False
        self.experimental = False
        self.standardized = True
        self.obsolete = False
        self.feature = None
        self.outer_td = None

    def process(self, cls, node, **kwargs):
        processed = super(CompatFeatureVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLElement):
            tag = processed.tag
            if tag == 'td':
                processed.drop_tag = True
                if self.outer_td:
                    self.add_issue(
                        'tag_dropped', self.outer_td.open_tag, tag='td',
                        scope=self.scope)
                self.outer_td = processed
            elif tag == 'br':
                processed.drop_tag = True  # Silently drop <br> tags
        elif isinstance(processed, Footnote):
            self.add_issue('footnote_feature', processed)
        elif isinstance(processed, DeprecatedInline):
            self.obsolete = True
        elif isinstance(processed, ObsoleteInline):
            self.obsolete = True
        elif isinstance(processed, ExperimentalInline):
            self.experimental = True
        elif isinstance(processed, (NonStandardInline, NotStandardInline)):
            self.standardized = False
        return processed

    def finalize_feature(self, td):
        """Finalize a new or updated feature."""
        name = td.to_html()
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
        assert self.outer_td
        self.finalize_feature(self.outer_td)
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
    """A version string, like '1.0', '1', or '1.0 (85.0)'."""

    def __init__(self, version, engine_version=None, **kwargs):
        super(CellVersion, self).__init__(**kwargs)
        self.version = format_version(version)
        self.engine_version = engine_version or None

    def __str__(self):
        if self.engine_version is None:
            return self.version
        else:
            return '{} ({})'.format(self.version, self.engine_version)


class CellRemoved(HTMLText):
    """The prefix text "Removed in"."""


class CellNoPrefix(HTMLText):
    """The suffix text (unprefixed) or (no prefix)."""


class CellPartial(HTMLText):
    """The suffix text (partial)."""


class CompatSupportVisitor(CompatBaseVisitor):
    scope = 'compatibility support'
    _allowed_tags = ['a', 'br', 'code', 'p', 'sup', 'td']

    def __init__(
            self, feature_id, browser_id, browser_name, browser_slug=None,
            **kwargs):
        """Initialize a CompatSupportVisitor.

        Keyword Arguments:
        feature_id - The feature ID for this row
        browser_id - The browser ID for this column
        browser_name - The browser name for this column
        browser_slug - The browser slug for this column
        """
        super(CompatSupportVisitor, self).__init__(**kwargs)
        self.feature_id = feature_id
        self.browser_id = browser_id
        self.browser_name = browser_name
        self.browser_slug = browser_slug or '<no slug>'
        self.versions = []
        self.supports = []
        self.inline_texts = []
        self.init_version_and_support()

    def init_version_and_support(self):
        self.version = {}
        self.provisional_version = None
        self.provisional_element = None
        self.support = {}

    def commit_support_and_version(self):
        """Commit new or updated support and version, and prepare for next."""
        if self.provisional_version and 'version' not in self.version:
            self.set_version(
                self.provisional_version, self.provisional_element)
        if self.version.get('version'):
            if (self.support.get('support') == 'yes' and
                    self.support.get('prefix') and
                    self.support.get('footnote_id')):
                # Footnote + prefix => support=partial
                self.support['support'] = 'partial'
            self.version['browser'] = self.browser_id
            self.support['feature'] = self.feature_id
            self.versions.append(self.version)
            self.supports.append(self.support)
            self.init_version_and_support()
        elif (self.version or self.support) and self.versions:
            self.versions[-1].update(self.version)
            self.supports[-1].update(self.support)
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
            elif tag == 'br':
                if self.version.get('version'):
                    self.commit_support_and_version()
        elif isinstance(processed, CellVersion):
            self.set_version(processed.version, processed)
        elif isinstance(processed, CompatVersionUnknown):
            self.set_version('current', processed)
        elif isinstance(processed, CompatNightly):
            self.set_version('nightly', processed)
        elif isinstance(processed, CompatNo):
            self.provisional_version = 'current'
            self.provisional_element = processed
            self.support['support'] = 'no'
        elif isinstance(processed, CompatUnknown):
            pass  # Don't record unknown support in API
        elif isinstance(processed, CompatGeckoFxOS):
            if not (processed.bad_version or processed.bad_override):
                self.set_version(str(processed.version), processed)
        elif isinstance(processed, CompatKumaScript):
            version_name = str(processed.version)
            if self.is_valid_version(version_name):
                self.set_version(version_name, processed)
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
            pass
        elif isinstance(processed, HTMLText):
            if processed.cleaned:
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
        ws1, version_node, ws2 = children
        version = version_node.match.group('version')
        engine_version = version_node.match.group('eng_version')
        return self.process(
            CellVersion, node, version=version, engine_version=engine_version)

    def visit_cell_removed(self, node, children):
        ws1, removed_node, ws2 = children
        return self.process(CellRemoved, removed_node)

    def visit_cell_noprefix(self, node, children):
        ws1, noprefix_choices, ws2 = children
        return self.process(CellNoPrefix, noprefix_choices[0])

    def visit_cell_partial(self, node, children):
        ws1, partial_choices, ws2 = children
        return self.process(CellPartial, partial_choices[0])


class CompatFootnoteVisitor(CompatBaseVisitor):
    scope = 'footnote'
    _allowed_tags = ['a', 'br', 'code', 'div', 'p', 'pre']

    def __init__(self, **kwargs):
        super(CompatFootnoteVisitor, self).__init__(**kwargs)
        self._footnote_data = OrderedDict()
        self._current_footnote_id = None
        self.embedded = []

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
            elif isinstance(child, EmbedCompatTable):
                self.embedded.append(child.arg(0))
            elif child.to_html():
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
            tag = processed.tag
            if tag in ('p', 'div'):
                self.gather_content(processed)
            elif tag == 'pre':
                self.process_pre(processed)
            elif tag in ('br', 'hr'):
                processed.drop_tag = True
        return processed

    def process_pre(self, pre_element):
        if self._current_footnote_id:
            self._footnote_data[self._current_footnote_id].append(
                (pre_element, True, pre_element.children))
        else:
            self.add_issue('footnote_no_id', pre_element)
