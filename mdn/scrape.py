"""Parsing Expression Grammar for MDN pages.

This code is messy. Parsing is messy. This may be related. It also, hopefully,
temporary, and will be jettisoned when the MDN data is imported.

The workflow is:
1. scrape_featurepage() takes a FeaturePage, which links an API Feature with
   an MDN page.  It passes the English raw page [1] plus the feature to:
2. scrape_page(), which extracts the specification and compatibility data
   from the page, by parsing it into a node tree with:
3. page_grammar, a parsing expression grammar in the Parsimonious [2] syntax,
   which is then passed to:
4. PageVisitor, which "visits" each node, extracting data, rendering
   KumaScript, matching to existing API features, and detecting errors.
5. The extracted data is returned to scrape_featurepage, which turns it into
   JSON-API in the view_feature format [3], with scrape-specific metadata.
6. The JSON can be used to view the scraped data, plan fixes to the MDN page,
   or be fed back into the API.

[1] https://developer.mozilla.org/en-US/docs/Web/API/CSSMediaRule?raw
[2] https://github.com/erikrose/parsimonious
[3] api/v1/view_features/1.json
"""
from __future__ import unicode_literals
from collections import OrderedDict
from copy import deepcopy
from itertools import chain
import re

from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type
from parsimonious import IncompleteParseError, ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

from webplatformcompat.models import (
    Browser, Feature, Section, Specification, Support, Version)
from .compatibility import (
    CompatFeatureVisitor, CompatFootnoteVisitor, CompatSupportVisitor,
    compat_feature_grammar, compat_footnote_grammar, compat_support_grammar)
from .html import HTMLText
from .kumascript import kumascript_grammar, KumaScript
from .specifications import Spec2Visitor, SpecDescVisitor, SpecNameVisitor
from .utils import is_new_id, slugify


# Parsimonious grammar for a raw MDN page
page_grammar = Grammar(
    r"""
# A whole raw MDN page
doc = other_text other_section* spec_section? compat_section?
    other_section* last_section?

# Sections that we don't care about
other_text = ~r".*?(?=<h2)"s
other_section = _ !(spec_h2 / compat_h2) other_h2 _ other_text
other_h2 = "<h2 " _ attrs? _ ">" _ ~r"(?P<content>.*?(?=</h2>))"s _ "</h2>"
last_section = _ other_h2 _ last_text
last_text =  ~r".*(?!=<h2)"s

#
# Specifications section
#
spec_section = _ spec_h2 _ (spec_table / whynospec)
spec_h2 = "<h2 " _ attrs? _ ">" _ spec_title _ "</h2>"
spec_title = ~r"(?P<content>[sS]pecifications?)"
whynospec = "<p>" _ whynospec_start whynospec_content whynospec_end "</p>" _
whynospec_start = ks_esc_start "WhyNoSpecStart" _ ks_esc_end _
whynospec_content = ~r".*?(?={{\s*WhyNoSpecEnd)"s
whynospec_end = ks_esc_start "WhyNoSpecEnd" _ ks_esc_end _
spec_table = "<table class=\"standard-table\">" _ spec_head _ spec_body
    _ "</table>" _

spec_head = spec_thead_headers / spec_tbody_headers
spec_thead_headers = "<thead>" _ spec_headers "</thead>" _ spec_tbody _
spec_tbody_headers = spec_tbody _ spec_headers
spec_headers =  "<tr>" _ th_elems _ "</tr>" _
spec_tbody = "<tbody>"

spec_body = spec_rows "</tbody>"
spec_rows = spec_row+
spec_row = tr_open _ specname_td _ spec2_td _ specdesc_td _ "</tr>" _
specname_td = td_open _ inner_td "</td>"
spec2_td = td_open _ inner_td "</td>"
specdesc_td = td_open _ inner_td "</td>"
inner_td = ~r"(?P<content>.*?(?=</td>))"s

#
# Browser Compatibility section
#
compat_section = _ compat_h2 _ compat_kumascript _ compat_divs
    compat_footnotes? compat_h3?
compat_h2 = "<h2 " _ attrs? _ ">" _ compat_title _ "</h2>"
compat_title = ~r"(?P<content>Browser [cC]ompat[ai]bility)"
compat_kumascript = (compat_kumascript_div / compat_kumascript_p)
compat_kumascript_div = "<div>" _ kumascript "</div>"
compat_kumascript_p = "<p>" _ kumascript "</p>"
compat_divs = compat_div+
compat_div = "<div" _ "id" _ equals _ compat_div_id ">" _ compat_table
    _ "</div>" _
compat_div_id = qtext
compat_table = "<table class=\"compat-table\">" _ compat_body _ "</table>" _
compat_body = "<tbody>" _ compat_headers _ compat_rows* _ "</tbody>"
compat_headers = tr_open _ feature_cell _ compat_client_cells _
    "</tr>" _
feature_cell = th_elem
compat_client_cells = th_elems
compat_rows = compat_row* _
compat_row = tr_open _ compat_row_cells _ "</tr>" _
compat_row_cells = compat_row_cell+
compat_row_cell = td_tag _

# TODO
th_elems = th_tag+

# UNTIL THEN
th_elems = th_elem+
th_elem = th_open _ (strong_text / bare_text) "</th>" _


#
# A cell in the Compat table
#   Due to rowspan and colspan usage, we won't know if a cell is a feature
#   or a support until we visit the table.
#
compat_cell = compat_cell_token*
compat_cell_token = html_content

#
# Optional footnotes after the Browser Compatibility Tables
#
compat_footnotes = html_content _
compat_h3 = "<h3 " _ attrs? _ ">" _ ~r"(?P<content>.*?(?=</h3>))"s _ "</h3>"
    (other_text / last_text)
#
# KumaScript tokens
#
kumascript = ks_esc_start ks_name ks_arglist? ks_esc_end
ks_esc_start = "{{" _
ks_name = ~r"(?P<content>[^\(\}\s]*)\s*"s
ks_arglist = ks_func_start ks_arg ks_arg_rest* ks_func_end
ks_func_start = "(" _
ks_func_arg = _ "," _
ks_func_end = _ ")" _
ks_esc_end = "}}" _
ks_arg = (double_quoted_text / single_quoted_text / ks_bare_arg)
ks_bare_arg = ~r"(?P<content>.*?(?=[,)]))"
ks_arg_rest = ks_func_arg ks_arg

#
# HTML tag attributes
#
attrs = attr+
opt_attrs = attr*
attr = _ ident _ equals _ qtext _
equals = "="
ident = ~r"(?P<content>[a-z][a-z0-9-:]*)"

#
# HTML tokens (only those used in compat tables)
#
html_content = html_block
html_block = html_tag+
html_tag = a_tag / break / code_tag / p_tag / pre_tag / span_tag / strong_tag /
    sup_tag / text_block

a_tag = a_open a_content "</a>"
a_open = "<a" _ opt_attrs ">"
a_content = html_content

break = "<" _ "br" _ ("/>" / ">") _

code_tag = code_open code_content "</code>" _
code_open = "<code" _ opt_attrs ">"
code_content = ~r"(?P<content>.*?(?=</code>))"s

p_tag = p_open p_content "</p>"
p_open = "<p" _ opt_attrs ">"
p_content = html_content

pre_tag = pre_open pre_content "</pre>"
pre_open = "<pre" _ opt_attrs ">"
pre_content = ~r"(?P<content>.*?(?=</pre>))"s

span_tag = span_open span_content "</span>"
span_open = "<span" _ opt_attrs ">"
span_content = html_content

strong_tag = strong_open strong_content "</strong>"
strong_open = "<strong" _ opt_attrs ">"
strong_content = html_content

sup_tag = sup_open sup_content "</sup>"
sup_open = "<sup" _ opt_attrs ">"
sup_content = html_content

table_tag = table_open table_content "</table>"
table_open = "<table" _ opt_attrs ">"
table_content = thead_tag / tbody_tag

tbody_tag = tbody_open tbody_content "</tbody>"
tbody_open = "<tbody" _ opt_attrs ">"
tbody_content = tr_tags

td_tag = td_open td_content "</td>"
td_open = "<td" _ opt_attrs ">"
td_content = html_content

th_tag = th_open th_content "</th>"
th_open = "<th" _ opt_attrs ">"
th_content = html_content

thead_tag = thead_open thead_content "</thead>"
thead_open = "<thead" _ opt_attrs ">"
thead_content = tr_tags

tr_tag = tr_open tr_contents "</tr>"
tr_open = "<tr" _ opt_attrs ">"
tr_contents = tr_content*
tr_content = td_tag / th_tag
tr_tags = tr_tag*

#
# Text segments
#
text_block = text_token+
text_token = kumascript / footnote_id / text_item
cell_version = ~r"(?P<version>\d+(\.\d+)*)"""
    r"""(\s+\((?P<eng_version>\d+(\.\d+)*)\))?\s*"s
footnote_id = "[" ~r"(?P<content>\d+|\*+)" "]"
text_item = ~r"(?P<content>[^{<[]+)\s*"s

text = (double_quoted_text / single_quoted_text / bare_text)
qtext = (double_quoted_text / single_quoted_text)
bare_text = ~r"(?P<content>[^<]*)"
strong_text = "<strong>" _ bare_text _ "</strong>" _
double_quoted_text = ~r'"(?P<content>[^"]*)"'
single_quoted_text = ~r"'(?P<content>[^']*)'"

# Whitespace
_ = ~r"[ \t\r\n]*"s
""")


@python_2_unicode_compatible
class EmptyString(object):
    """Non-falsy placeholder for empty string"""

    def __str__(self):
        return text_type('')


class PageVisitor(NodeVisitor):
    """Extract and validate data from a parsed MDN page.

    visit_<rule> is the function called when a node matching a rule is
    visited.  For reference, visit_* functions are roughly in the order
    they appear in page_grammar.

    When visiting a full document, the desired output is a dictionary
    with the keys:

    - 'locale': The locale of the page (passed in)
    - 'specs': Data scraped from Specifications section
    - 'compat': Data scraped from the Browser Compatibility table
    - 'footnotes': Footnotes appearing after the Browser Compatibility table,
      but not referenced in the table
    - 'issues': Issues with the parsed page
    """
    def __init__(self, feature, locale='en'):
        super(PageVisitor, self).__init__()
        self.feature = feature
        assert isinstance(feature, Feature), type(feature)
        self.locale = locale
        self.specs = []
        self.issues = []
        self.compat = []
        self.footnotes = None
        self._browser_data = None
        self._feature_data = None

    def generic_visit(self, node, visited_children):
        """Visitor when none is specified."""
        return visited_children or node

    def kumascript_grammar(self):
        if not hasattr(self, '_kumascript_grammar'):  # pragma: no branch
            self._kumascript_grammar = Grammar(kumascript_grammar)
        return self._kumascript_grammar

    def compat_feature_grammar(self):
        if not hasattr(self, '_compat_feature_grammar'):  # pragma: no branch
            self._compat_feature_grammar = Grammar(compat_feature_grammar)
        return self._compat_feature_grammar

    def compat_support_grammar(self):
        if not hasattr(self, '_compat_support_grammar'):  # pragma: no branch
            self._compat_support_grammar = Grammar(compat_support_grammar)
        return self._compat_support_grammar

    def compat_footnote_grammar(self):
        if not hasattr(self, '_compat_footnote_grammar'):  # pragma: no branch
            self._compat_footnote_grammar = Grammar(compat_footnote_grammar)
        return self._compat_footnote_grammar

    def _visit_content(self, node, children):
        """Visitor for re nodes with a named (?P<content>) section."""
        return node.match.group('content')

    def _visit_content_item(self, node, children):
        """Visitor for converting re content into items."""
        return {
            "type": "text", "start": node.start, "end": node.end,
            "content": self._visit_content(node, children)}

    def _visit_token(self, node, children):
        """Visitor for one of many tokenized items"""
        token = children[0]
        assert isinstance(token, dict), type(token)
        return token

    def visit_doc(self, node, children):
        """At the top level, return all the collected data."""
        return {
            'specs': self.specs,
            'locale': self.locale,
            'issues': self.issues,
            'compat': self.compat,
            'footnotes': self.footnotes,
        }

    re_h2 = re.compile(r'''(?x)(?s)     # Be verbose, and don't stop at newline
    <h2[^>]*>           # Look for h2 open tag
    (?P<title>[^<]+)    # Capture the h2 title
    </h2>               # The h2 close tag
    ''')

    def visit_other_section(self, section_node, children):
        """Find "other" sections that should have been parsed.

        Because spec_section and compat_section are optional,
        unexpected elements cause them to be treated as other sections.
        This turns these into errors for further cleanp.
        """
        sections = {
            'browser compatibility': 'compat_section',
            'specifications': 'spec_section',
            'specification': 'spec_section'
        }

        for h2 in self.re_h2.finditer(section_node.text):
            title = h2.group('title')
            section = sections.get(title.lower().strip())
            if section:
                # Failed to parse an <h2>.  Add an error
                start = section_node.start + h2.start()
                text = section_node.text[h2.start():]
                try:
                    page_grammar[section].parse(text)
                except ParseError as pe:
                    expr = pe.expr
                    self.issues.append((
                        'section_skipped',
                        pe.pos + start, end_of_line(pe.text, pe.pos) + start,
                        {'rule_name': expr.name, 'title': title,
                         'rule': expr.as_rule()}))
                else:
                    self.issues.append((
                        'section_missed',
                        start,
                        end_of_line(text, 0) + start,
                        {'title': title}))

    visit_last_section = visit_other_section

    #
    # Specification section
    #
    def visit_spec_h2(self, node, children):
        attrs_list = children[2][0]
        assert isinstance(attrs_list, list), type(attrs_list)
        h2_id = None
        expected = ('Specifications', 'Specification')
        for attr in attrs_list:
            assert isinstance(attr, dict), type(attr)
            if attr['ident'] == 'id':
                h2_id = attr['value']
                if h2_id not in expected:
                    self.issues.append((
                        'spec_h2_id', attr['start'], attr['end'],
                        {'h2_id': h2_id}))
            elif attr['ident'] == 'name':
                h2_name = attr['value']
                if h2_name not in expected:
                    self.issues.append((
                        'spec_h2_name', attr['start'], attr['end'],
                        {'h2_name': h2_name}))

    def visit_spec_row(self, node, children):
        specname = children[2]
        assert isinstance(specname, tuple), type(specname)
        key, spec_id, path, name = specname

        spec2 = children[4]
        if isinstance(spec2, text_type):
            # Standard Spec2 KumaScript
            if spec2 and spec2 != key:
                self.issues.append((
                    'spec_mismatch', node.start, node.end,
                    {'spec2_key': spec2, 'specname_key': key}))
        else:
            # Text like 'Standard'
            assert isinstance(spec2, HTMLText), spec2
            self.issues.append((
                'spec2_converted', spec2.start, spec2.end,
                {'key': key, 'original': spec2.cleaned}))

        desc = children[6]
        assert isinstance(desc, text_type)

        section_id = None
        if spec_id:
            for section in Section.objects.filter(specification_id=spec_id):
                if section.subpath.get(self.locale) == path:
                    section_id = section.id
                    break
        self.specs.append({
            'specification.mdn_key': key,
            'specification.id': spec_id,
            'section.subpath': path,
            'section.name': name,
            'section.note': self.cleanup_whitespace(desc),
            'section.id': section_id})

    def visit_specname_td(self, node, children):
        raw_text = node.text
        reparsed = self.kumascript_grammar().parse(raw_text)
        visitor = SpecNameVisitor(offset=node.start)
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.issues.append(issue)

        key = visitor.mdn_key or ""
        if visitor.spec:
            spec_id = visitor.spec.id
        else:
            spec_id = None
        subpath = visitor.subpath or ""
        name = visitor.section_name or ""
        return (key, spec_id, subpath, name)

    def visit_spec2_td(self, node, children):
        raw_text = node.text
        reparsed = self.kumascript_grammar().parse(raw_text)
        visitor = Spec2Visitor(offset=node.start)
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.issues.append(issue)
        if visitor.mdn_key:
            return visitor.mdn_key
        else:
            item = visitor.spec2_item
            assert item
            if isinstance(item, HTMLText) and not isinstance(item, KumaScript):
                # Handle spec2 = text at row level
                return item
        return ""

    def visit_specdesc_td(self, node, children):
        raw_text = node.text
        reparsed = self.kumascript_grammar().parse(raw_text)
        visitor = SpecDescVisitor(offset=node.start)
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.issues.append(issue)
        html = [item.to_html() for item in visitor.desc_items]
        return self.join_content(html)

    def visit_inner_td(self, node, children):
        text = self.cleanup_whitespace(node.text)
        assert 'td>' not in text
        return {
            'type': 'text', 'content': text,
            'start': node.start, 'end': node.end}

    #
    # Browser Compatibility section
    #
    def visit_compat_section(self, node, children):
        compat_divs = children[5]
        footnote_node = children[6]
        if isinstance(footnote_node, Node):
            assert footnote_node.start == footnote_node.end  # Empty
            footnotes = OrderedDict()
        else:
            footnotes = footnote_node[0]

        assert isinstance(compat_divs, list), type(compat_divs)
        for div in compat_divs:
            assert isinstance(div, dict), type(div)
        assert isinstance(footnotes, OrderedDict), type(footnotes)

        # Merge footnotes into supports
        used_footnotes = set()
        for div in compat_divs:
            for support in div['supports']:
                if 'footnote_id' in support:
                    f_id, f_start, f_end = support['footnote_id']
                    try:
                        text, start, end = footnotes[f_id]
                    except KeyError:
                        self.issues.append((
                            'footnote_missing', f_start, f_end,
                            {'footnote_id': f_id}))
                    else:
                        support['footnote'] = text
                        used_footnotes.add(f_id)

        for f_id in used_footnotes:
            del footnotes[f_id]

        for f_id, (text, start, end) in footnotes.items():
            self.issues.append((
                'footnote_unused', start, end, {'footnote_id': f_id}))

        self.compat = compat_divs
        self.footnotes = footnotes

    def visit_compat_kumascript(self, node, children):
        assert isinstance(children, list), type(children)
        kumascript = children[0][2]
        assert isinstance(kumascript, dict), type(kumascript)
        assert kumascript['type'] == 'kumascript'
        assert kumascript['name'].lower() == 'compatibilitytable'

    def visit_compat_div(self, node, children):
        compat_div_id = children[6][0]
        compat_table = children[9]

        pre, div_id = compat_div_id.split('-', 1)
        assert isinstance(div_id, text_type), type(div_id)
        assert isinstance(compat_table, dict), type(compat_table)

        div = compat_table.copy()
        div['name'] = div_id
        return div

    def visit_compat_table(self, node, children):
        compat_body = children[2]
        assert isinstance(compat_body, dict), type(compat_body)
        return compat_body

    def visit_compat_body(self, node, children):
        compat_headers = children[2]
        compat_rows = children[4][0]

        assert isinstance(compat_headers, list), type(compat_headers)
        for header in compat_headers:
            assert isinstance(header, dict), type(header)
        assert isinstance(compat_rows, list), type(compat_rows)
        for row in compat_rows:
            assert isinstance(row, dict), type(row)

        browsers = OrderedDict()
        features = OrderedDict()
        versions = OrderedDict()
        supports = OrderedDict()

        # Gather the browsers and determine # of columns
        columns = [None]
        for browser in compat_headers:
            colspan = int(browser.pop('colspan', 1))
            browser_id = browser['id']
            browsers[browser_id] = browser
            for i in range(colspan):
                columns.append(browser_id)

        # Create an empty row grid
        table = []
        for row in range(len(compat_rows)):
            table_row = []
            for col in range(len(columns)):
                table_row.append(None)
            table.append(table_row)

        # Parse the rows for features and supports
        for row, compat_row in enumerate(compat_rows):
            for cell in compat_row['cells']:
                td = cell
                try:
                    col = table[row].index(None)
                except ValueError:
                    self.issues.append((
                        'extra_cell', td['start'], cell['end'], {}))
                    continue
                rowspan = int(td.get('rowspan', 1))
                colspan = int(td.get('colspan', 1))
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
                    browser_id = columns[col]
                    browser = browsers[browser_id]
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
                        table[row + r][col + c] = cell_id

        return {
            'browsers': list(browsers.values()),
            'versions': list(versions.values()),
            'features': list(features.values()),
            'supports': list(supports.values()),
        }

    def visit_compat_headers(self, node, children):
        feature = children[2]
        compat_client_cells = children[4]
        assert isinstance(feature, dict), type(feature)
        assert isinstance(compat_client_cells, list), type(compat_client_cells)

        # Verify feature header
        fcontent = feature['content']
        if fcontent['text'] != 'Feature':
            self.issues.append((
                'feature_header', fcontent['start'], fcontent['end'],
                {'header': fcontent['text']}))

        # Process client headers
        expected_attrs = ('colspan',)
        clients = []
        for raw_cell in compat_client_cells:
            assert isinstance(raw_cell, dict), type(raw_cell)
            assert raw_cell['type'] == 'th'
            cell = self._consume_attributes(raw_cell, expected_attrs)
            content = cell['content']
            name = content['text']
            assert isinstance(name, text_type), type(name)
            b_id, b_name, b_slug = self.browser_id_name_and_slug(name)
            if is_new_id(b_id):
                self.issues.append((
                    'unknown_browser', content['start'], content['end'],
                    {'name': name}))
            client = {
                'name': b_name,
                'id': b_id,
                'slug': b_slug
            }
            if 'colspan' in cell:
                client['colspan'] = cell['colspan']
            clients.append(client)

        return clients

    def visit_compat_rows(self, node, children):
        compat_rows = children[0]

        assert isinstance(compat_rows, list), type(compat_rows)
        for row in compat_rows:
            assert isinstance(row, dict), type(row)
        return compat_rows

    def visit_compat_row(self, node, children):
        tr_open = children[0]
        compat_row_cells = children[2]

        assert isinstance(tr_open, dict), type(tr_open)
        assert isinstance(compat_row_cells, list), type(compat_row_cells)
        for cell in compat_row_cells:
            assert isinstance(cell, dict), type(cell)
        row_dict = {'cells': compat_row_cells}
        row_dict.update(tr_open)
        return row_dict

    def visit_compat_row_cell(self, node, children):
        td_tag = children[0]
        assert isinstance(td_tag, dict), type(td_tag)
        assert td_tag['type'] == 'td'
        compat_row = (
            self._consume_attributes(td_tag, ('rowspan', 'colspan')))
        compat_row['raw'] = node.text
        return compat_row

    visit_compat_cell_token = _visit_token

    #
    # Optional footnotes after the Browser Compatibility Tables
    #

    def visit_compat_footnotes(self, node, children):
        """Parse footnote section."""
        raw_text = node.text
        reparsed = self.compat_footnote_grammar().parse(raw_text)
        visitor = CompatFootnoteVisitor(offset=node.start)
        visitor.visit(reparsed)
        footnotes = visitor.finalize_footnotes()
        for issue in visitor.issues:
            self.issues.append(issue)
        return footnotes

    def visit_footnote_id(self, node, children):
        raw_id = children[1].match.group('content')
        if raw_id.isnumeric():
            footnote_id = raw_id
        else:
            footnote_id = text_type(len(raw_id))
        return {
            'type': 'footnote_id',
            'footnote_id': footnote_id,
            'start': node.start, 'end': node.end}

    def visit_compat_h3(self, node, children):
        title = children[6].text.strip()
        h3_end = children[8]
        self.issues.append(
            ('skipped_h3', node.start, h3_end.end, {'h3': title}))

    #
    # KumaScript Tokens
    #
    def visit_kumascript(self, node, children):
        name = children[1]
        assert isinstance(name, text_type), type(name)

        argslist = children[2]
        if isinstance(argslist, Node):
            assert argslist.start == argslist.end
            args = []
        else:
            assert isinstance(argslist, list), type(argslist)
            assert len(argslist) == 1
            args = argslist[0]
        assert isinstance(args, list), type(args)
        if args == ['']:
            args = []

        return {
            'type': 'kumascript', 'name': name, 'args': args,
            'start': node.start, 'end': node.end}

    visit_ks_name = _visit_content

    def visit_ks_arglist(self, node, children):
        arg0 = children[1]
        argrest = children[2]
        args = [arg0]
        if isinstance(argrest, Node):
            # No additional args
            assert argrest.start == argrest.end
        else:
            for _, arg in argrest:
                args.append(arg)
        arglist = [text_type(a) for a in args]
        return arglist

    def visit_ks_arg(self, node, children):
        assert isinstance(children, list)
        assert len(children) == 1
        item = children[0]
        assert isinstance(item, text_type)
        return item or EmptyString()

    visit_ks_bare_arg = _visit_content

    #
    # Attribute processing
    #

    def visit_attrs(self, node, children):
        return children  # Even if empty list

    visit_opt_attrs = visit_attrs

    def visit_attr(self, node, children):
        ident = children[1]
        value = children[5][0]

        assert isinstance(ident, text_type), type(ident)
        assert isinstance(value, text_type), type(value)

        return {
            'ident': ident,
            'value': value,
            'start': node.start,
            'end': node.end,
        }

    visit_ident = _visit_content
    visit_bare_text = _visit_content
    visit_text_item = _visit_content_item
    visit_single_quoted_text = _visit_content
    visit_double_quoted_text = _visit_content

    #
    # HTML tokens
    #
    visit_html_tag = _visit_token

    def visit_html_block(self, node, children):
        assert children
        for child in children:
            assert isinstance(child, dict), type(child)
        if len(children) == 1:
            return children[0]
        else:
            return {
                'type': 'html_block',
                'start': node.start,
                'end': node.end,
                'content': children
            }

    def _visit_open(self, node, children):
        """Parse an opening tag with an optional attributes list"""
        open_tag_node = children[0]
        assert isinstance(open_tag_node, Node), type(open_tag_node)
        open_tag = open_tag_node.text
        assert open_tag.startswith('<')
        tag = open_tag[1:]

        attrs = children[2]
        assert isinstance(attrs, list), type(attrs)
        for attr in attrs:
            assert isinstance(attr, dict)

        # Index by attribute ident
        attr_dict = {}
        for attr in attrs:
            ident = attr.pop('ident')
            assert ident not in attr_dict
            attr_dict[ident] = attr

        return {
            'type': tag,
            'attributes': attr_dict,
            'start': node.start,
            'end': node.end,
        }

    visit_a_open = _visit_open
    visit_td_open = _visit_open
    visit_th_open = _visit_open
    visit_tr_open = _visit_open
    visit_p_open = _visit_open
    visit_pre_open = _visit_open
    visit_span_open = _visit_open
    visit_strong_open = _visit_open
    visit_sup_open = _visit_open
    visit_code_open = _visit_open

    def visit_break(self, node, children):
        return {'type': 'break', 'start': node.start, 'end': node.end}

    def _visit_tag(self, node, children):
        """Parse a <tag>content</tag> block."""
        tag_open = children[0]
        content = children[1]
        tag_close = children[2]
        assert isinstance(tag_close, Node)
        assert isinstance(content, dict), type(content)

        tag = deepcopy(tag_open)
        tag['end'] = tag_close.end
        tag['content'] = content
        return tag

    visit_a_tag = _visit_tag
    visit_code_tag = _visit_tag
    visit_p_tag = _visit_tag
    visit_pre_tag = _visit_tag
    visit_span_tag = _visit_tag
    visit_strong_tag = _visit_tag
    visit_sup_tag = _visit_tag
    visit_table_tag = _visit_tag
    visit_tbody_tag = _visit_tag
    visit_td_tag = _visit_tag
    visit_th_tag = _visit_tag
    visit_thead_tag = _visit_tag
    visit_tr_tag = _visit_tag

    visit_pre_content = _visit_content_item
    visit_code_content = _visit_content_item

    #
    # HTML tag attributes
    #

    def _consume_attributes(self, node_dict, expected):
        """Move attributes to node dict, or add issue."""
        node_out = node_dict.copy()
        attrs = node_out.pop('attributes', {})
        for ident, attr in attrs.items():
            if ident in expected:
                assert ident not in node_out
                node_out[ident] = attr['value']
            else:
                if len(expected) > 1:
                    expected_text = (
                        'the attributes ' + ', '.join(expected[:-1]) + ' or ' +
                        expected[-1])
                else:
                    assert len(expected) == 1
                    expected_text = 'the attribute ' + expected[0]
                """
                else:
                    expected_text = 'no attributes'
                """
                self.issues.append((
                    'unexpected_attribute', attr['start'], attr['end'],
                    {'node_type': node_dict['type'], 'ident': ident,
                        'value': attr['value'], 'expected': expected_text}))
        return node_out

    #
    # Text segments
    #

    def visit_th_elem(self, node, children):
        th_open = children[0]
        content = children[2][0]
        assert isinstance(th_open, dict), type(th_open)
        if isinstance(content, dict):
            th_open['content'] = content
        else:
            assert isinstance(content, text_type)
            th_open['content'] = {
                'start': children[1].end,
                'end': children[3].start,
                'text': self.cleanup_whitespace(content)
            }
        return th_open

    def visit_strong_text(self, node, children):
        text = children[2]
        assert isinstance(text, text_type), type(text)
        return {
            'start': children[1].end,
            'end': children[3].start,
            'text': self.cleanup_whitespace(text),
            'strong': True
        }

    def visit_text_block(self, node, children):
        assert children
        for child in children:
            assert isinstance(child, dict), type(child)
        if len(children) == 1:
            return children[0]
        else:
            return {
                'type': 'text_block',
                'start': node.start,
                'end': node.end,
                'content': children
            }

    visit_text_token = _visit_token

    #
    # Utility methods
    #
    re_whitespace = re.compile(r'''(?x)  # Be verbose
    (\s|                # Any whitespace, or
     (<\s*br\s*/?>)|    # A variant of <br>, or
     \xa0|              # Unicode non-breaking space, or
     (\&nbsp;)          # HTML nbsp character
    )+                  # One or more in a row
    ''')

    def cleanup_whitespace(self, text):
        """Normalize whitespace"""
        normal = self.re_whitespace.sub(' ', text)
        assert '  ' not in normal
        return normal.strip()

    def unquote(self, text):
        """Unquote strings."""
        if text.startswith('"') or text.startswith("'"):
            if text[0] == text[-1]:
                return text[1:-1]
            elif (text.count(text[0]) % 2) != 0:
                raise ValueError(text)
        return text

    def kumascript_issue(self, issue, item, scope):
        """Create an kumascript issue."""
        if item['args']:
            args = '(' + ', '.join(item['args']) + ')'
        else:  # pragma: no cover
            args = ''
        return (
            issue, item['start'], item['end'],
            {'name': item['name'], 'args': item['args'], 'scope': scope,
             'kumascript': "{{%s%s}}" % (item['name'], args)})

    def kumascript_to_html(self, item, scope):
        """Convert kumascript to plain HTML.

        TODO: remove code when HTML conversion moved to kumascript.py
        """
        assert item['type'] == 'kumascript'
        name = item['name']
        args = item['args']
        if name in (
                'xref_csslength', 'xref_csspercentage',
                'xref_cssstring', 'xref_cssimage'):
            assert not args
            content = name[len('xref_css'):]
            return "<code>&lt;{}&gt;</code>".format(content)
        elif name == 'xref_csscolorvalue':
            assert not args
            return "<code>&lt;color&gt;</code>"
        elif name == 'xref_cssvisual':
            assert not args
            return "<code>visual</code>"
        elif name.lower() in ('cssxref', 'domxref', 'jsxref'):
            assert len(args) < 3  # domxref does funky stuff w/ args 3 and 4
            if len(args) == 2:
                content = args[1]
            else:
                content = args[0]
            return "<code>{}</code>".format(content)
        elif name.lower() == 'htmlelement':
            content = args[0]
            if ' ' in content:
                return "<code>{}</code>".format(content)
            else:
                return "<code>&lt;{}&gt;</code>".format(content)
        elif name.lower() == 'specname':
            assert len(args) >= 1
            return 'specification ' + args[0]
        else:
            self.issues.append(
                self.kumascript_issue('unknown_kumascript', item, scope))

    def join_content(self, content_bits):
        """Construct a string with just the right whitespace."""
        out = ""
        nospace_before = '!,.;? '
        nospace_after = ' '
        strip_next = False
        for bit in content_bits:
            if bit:
                if (out and out[-1] not in nospace_after and
                        bit[0] not in nospace_before and not strip_next):
                    out += " "
                strip_next = False
                out += bit
        return out

    #
    # API lookup methods
    #
    browser_name_fixes = {
        'Firefox (Gecko)': 'Firefox',
        'Firefox Mobile (Gecko)': 'Firefox Mobile',
        'Firefox OS (Gecko)': 'Firefox OS',
        'Safari (WebKit)': 'Safari',
        'Windows Phone': 'IE Mobile',
        'IE Phone': 'IE Mobile',
        'IE': 'Internet Explorer',
    }

    def browser_id_name_and_slug(self, name):
        # Normalize the name
        nname = self.cleanup_whitespace(name)
        fixed_name = self.browser_name_fixes.get(nname, nname)

        # Load existing browser data
        if self._browser_data is None:
            self._browser_data = {}
            for browser in Browser.objects.all():
                key = browser.name[self.locale]
                self._browser_data[key] = (browser.pk, key, browser.slug)

        # Select the Browser ID and slug
        if fixed_name not in self._browser_data:
            browser_id = '_' + nname
            self._browser_data[fixed_name] = (
                browser_id, fixed_name, browser_id)
        return self._browser_data[fixed_name]

    def feature_id_and_slug(self, name):
        """Get or create the feature ID and slug given a name."""
        def normalized(name):
            """Normalize a name for IDs, slugs."""
            to_remove = ('<code>', '</code>', '&lt;', '&gt;')
            normalized_name = name.lower()
            for removal in to_remove:
                normalized_name = normalized_name.replace(removal, '')
            return normalized_name
        nname = normalized(name)

        # Initialize Feature IDs
        if self._feature_data is None:
            self._feature_data = {}
            for feature in Feature.objects.filter(parent=self.feature):
                assert 'zxx' not in feature.name
                fname = feature.name.get(self.locale, feature.name['en'])
                fname = normalized(fname)
                self._feature_data[fname] = (feature.id, feature.slug)

        # Select the Feature ID and slug
        if nname not in self._feature_data:
            feature_id = '_' + nname
            attempt = 0
            feature_slug = None
            while not feature_slug:
                base_slug = self.feature.slug + '_' + nname
                feature_slug = slugify(base_slug, suffix=attempt)
                if Feature.objects.filter(slug=feature_slug).exists():
                    attempt += 1
                    feature_slug = ''
            self._feature_data[nname] = (feature_id, feature_slug)

        return self._feature_data[nname]

    #
    # Cell parsing
    #

    def cell_to_feature(self, cell):
        """Parse cell items as a feature (first column)"""
        raw_text = cell['raw']
        reparsed = self.compat_feature_grammar().parse(raw_text)
        visitor = CompatFeatureVisitor(
            parent_feature=self.feature, offset=cell['start'])
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.issues.append(issue)
        feature = visitor.to_feature_dict()
        return feature

    def cell_to_support(self, cell, feature, browser):
        """Parse a cell as a support (middle cell)."""
        raw_text = cell['raw']
        reparsed = self.compat_support_grammar().parse(raw_text)
        visitor = CompatSupportVisitor(
            feature_id=feature['id'], browser_id=browser['id'],
            browser_name=browser['name'], browser_slug=browser['slug'],
            offset=cell['start'])
        visitor.visit(reparsed)
        for issue in visitor.issues:
            self.issues.append(issue)
        return visitor.versions, visitor.supports


def scrape_page(mdn_page, feature, locale='en'):
    data = OrderedDict((
        ('locale', locale),
        ('specs', []),
        ('compat', []),
        ('footnotes', None),
        ('issues', []),
    ))

    # Quick check for data in page
    if not (
            ('Browser compatibility</h' in mdn_page) or
            ('Specifications</h' in mdn_page) or
            ('CompatibilityTable' in mdn_page)):
        return data

    try:
        page_parsed = page_grammar.parse(mdn_page)
    except IncompleteParseError as ipe:
        data['issues'].append((
            'halt_import', ipe.pos, end_of_line(ipe.text, ipe.pos), {}))
        return data
    except ParseError as pe:
        if pe.expr.name == 'doc':
            data['issues'].append((
                'doc_parse_error', pe.pos, end_of_line(pe.text, pe.pos), {}))
            return data
        else:  # pragma: no cover
            # Raise as 'exception' issue to flag for future work
            raise pe

    page_data = PageVisitor(feature).visit(page_parsed)

    data['specs'] = page_data.get('specs', [])
    data['compat'] = page_data.get('compat', [])
    data['issues'] = page_data.get('issues', [])
    data['footnotes'] = page_data.get('footnotes', None)
    return data


class ScrapedViewFeature(object):
    """Combine a scraped MDN page with existing API data.

    This code works with scraping of English feature pages that aren't
    already in the API. Modifications may be needed to:
    - Update API resources from updated MDN pages
    - Scrape pages in non-English languages
    """

    tab_name = {
        'desktop': 'Desktop Browsers',
        'mobile': 'Mobile Browsers',
    }

    def __init__(self, feature_page, scraped_data):
        self.feature_page = feature_page
        self.feature = feature_page.feature
        self.scraped_data = scraped_data
        self.resources = OrderedDict()
        for resource_type in (
                'specifications', 'maturities', 'sections', 'browsers',
                'versions', 'features', 'supports'):
            self.resources[resource_type] = {}
        self.tabs = []
        self.compat_table_supports = OrderedDict(
            ((text_type(self.feature.id), {}),))
        self.notes = OrderedDict()

    def generate_data(self):
        """Combine the page and scraped data into view_feature structure."""
        fp_data = self.feature_page.reset_data()
        fp_data['meta']['scrape']['raw'] = self.scraped_data

        for spec_row in self.scraped_data['specs']:
            self.load_specification_row(spec_row)
        for table in self.scraped_data['compat']:
            self.load_compat_table(table)
        for section in self.resources['sections'].values():
            fp_data['features']['links']['sections'].append(section['id'])

        for resource_type, resources in self.resources.items():
            fp_data['linked'][resource_type] = self.sort_values(resources)
        languages = fp_data['features']['mdn_uri'].keys()
        fp_data['meta']['compat_table']['languages'] = list(languages)
        fp_data['meta']['compat_table']['tabs'] = self.tabs
        fp_data['meta']['compat_table']['supports'] = (
            self.compat_table_supports)
        fp_data['meta']['compat_table']['notes'] = self.notes
        return fp_data

    def load_specification_row(self, spec_row):
        """Load Specification, Maturity, and Section"""
        # Load Specification and Maturity
        if spec_row['specification.id']:
            spec_content, mat_content = self.load_specification(
                spec_row['specification.id'])
        else:
            spec_content, mat_content = self.new_specification(spec_row)
        self.add_resource('specifications', spec_content)
        self.add_resource('maturities', mat_content)

        # Load Specification Section
        if spec_row['section.id']:
            section_content = self.load_section(spec_row['section.id'])
            section_content['name']['en'] = spec_row['section.name']
            section_content['subpath']['en'] = spec_row['section.subpath']
            section_content['note']['en'] = spec_row['section.note']
        else:
            section_content = self.new_section(spec_row, spec_content['id'])
        self.add_resource('sections', section_content)

    def load_compat_table(self, table):
        """Load a compat table."""
        tab = OrderedDict((
            ("name",
             {"en": self.tab_name.get(table['name'], 'Other Environments')}),
            ("browsers", []),
        ))
        # Load Browsers (first row)
        for browser_entry in table['browsers']:
            if is_new_id(browser_entry['id']):
                browser_content = self.new_browser(browser_entry)
            else:
                browser_content = self.load_browser(browser_entry['id'])
            self.add_resource('browsers', browser_content)
            tab['browsers'].append(text_type(browser_content['id']))

        # Load Features (first column)
        for feature_entry in table['features']:
            if is_new_id(feature_entry['id']):
                feature_content = self.new_feature(feature_entry)
            else:
                feature_content = self.load_feature(feature_entry['id'])
            self.add_resource_if_new('features', feature_content)
            self.compat_table_supports.setdefault(
                text_type(feature_content['id']), OrderedDict())

        # Load Versions (explicit or implied in cells)
        for version_entry in table['versions']:
            if is_new_id(version_entry['id']):
                version_content = self.new_version(version_entry)
            else:
                version_content = self.load_version(version_entry['id'])
            self.add_resource_if_new('versions', version_content)

        # Load Supports (cells)
        for support_entry in table['supports']:
            if is_new_id(support_entry['id']):
                support_content = self.new_support(support_entry)
            else:
                support_content = self.load_support(support_entry['id'])
            self.add_resource_if_new('supports', support_content)
            if support_content['note']:
                note_id = len(self.notes) + 1
                self.notes[support_content['id']] = note_id

            # Set the meta lookup
            version = self.get_resource(
                'versions', support_content['links']['version'])
            feature_id = support_content['links']['feature']
            browser_id = version['links']['browser']
            supports = self.compat_table_supports[feature_id]
            supports.setdefault(browser_id, [])
            supports[browser_id].append(support_entry['id'])
        self.tabs.append(tab)

    def add_resource(self, resource_type, content):
        """Add a linked resource, replacing any existing resource."""
        resource_id = content['id']
        self.resources[resource_type][resource_id] = content

    def add_resource_if_new(self, resource_type, content):
        """Add a linked resource only if there is no existing resource."""
        resource_id = content['id']
        return self.resources[resource_type].setdefault(resource_id, content)

    def get_resource(self, resource_type, resource_id):
        """Get an existing linked resource."""
        return self.resources[resource_type][resource_id]

    def sort_values(self, d):
        """Return dictionary values, sorted by keys."""
        existing_keys = sorted([k for k in d.keys() if not is_new_id(k)])
        new_keys = sorted([k for k in d.keys() if is_new_id(k)])
        return list(d[k] for k in chain(existing_keys, new_keys))

    def load_specification(self, spec_id):
        """Serialize an existing specification."""
        spec = Specification.objects.get(id=spec_id)
        section_ids = [
            text_type(s_id) for s_id in spec.sections.values_list(
                'id', flat=True)]
        spec_content = OrderedDict((
            ('id', text_type(spec_id)),
            ('slug', spec.slug),
            ('mdn_key', spec.mdn_key),
            ('name', spec.name),
            ('uri', spec.uri),
            ('links', OrderedDict((
                ('maturity', text_type(spec.maturity_id)),
                ('sections', section_ids)
            )))))
        mat = spec.maturity
        mat_content = OrderedDict((
            ('id', text_type(mat.id)),
            ('slug', mat.slug),
            ('name', mat.name)))
        return spec_content, mat_content

    def new_specification(self, spec_row):
        """Serialize a new specification."""
        spec_id = '_' + spec_row['specification.mdn_key']
        mat_id = '_unknown'
        spec_content = OrderedDict((
            ('id', spec_id),
            ('mdn_key', spec_row['specification.mdn_key']),
            ('links', OrderedDict((
                ('maturity', mat_id),
                ('sections', [])
            )))))
        mat_content = self.add_resource_if_new(
            'maturities', OrderedDict((
                ('id', mat_id),
                ('slug', ''),
                ('name', {'en': 'Unknown'}),
                ('links', {'specifications': []}))))
        return spec_content, mat_content

    def load_section(self, section_id):
        """Serialize an existing section."""
        section = Section.objects.get(id=section_id)
        section_content = OrderedDict((
            ('id', text_type(section_id)),
            ('number', section.number or None),
            ('name', section.name),
            ('subpath', section.subpath),
            ('note', section.note),
            ('links', OrderedDict((
                ('specification', text_type(section.specification_id)),)))))
        return section_content

    def new_section(self, spec_row, spec_id):
        """Serialize a new section."""
        section_id = text_type(spec_id) + '_' + spec_row['section.subpath']
        section_content = OrderedDict((
            ('id', section_id),
            ('number', None),
            ('name', OrderedDict()),
            ('subpath', OrderedDict()),
            ('note', OrderedDict()),
            ('links', OrderedDict((
                ('specification', text_type(spec_id)),)))))
        section_content['name']['en'] = spec_row['section.name']
        section_content['subpath']['en'] = spec_row['section.subpath']
        section_content['note']['en'] = spec_row['section.note']
        return section_content

    def load_browser(self, browser_id):
        """Serialize an existing browser."""
        browser = Browser.objects.get(id=browser_id)
        browser_content = OrderedDict((
            ('id', text_type(browser.id)),
            ('slug', browser.slug),
            ('name', browser.name),
            ('note', browser.note or None),
        ))
        return browser_content

    def new_browser(self, browser_entry):
        """Serialize a new browser."""
        browser_content = OrderedDict((
            ('id', browser_entry['id']),
            ('slug', ''),
            ('name', {'en': browser_entry['name']}),
            ('note', None),
        ))
        return browser_content

    def load_feature(self, feature_id):
        """Serialize an existing feature."""
        feature = Feature.objects.get(id=feature_id)
        section_ids = [
            text_type(s_id) for s_id in
            feature.sections.values_list('pk', flat=True)]
        support_ids = [
            text_type(s_id) for s_id in
            sorted(feature.supports.values_list('pk', flat=True))]
        parent_id = (
            text_type(feature.parent_id) if feature.parent_id
            else None)
        children_ids = [
            text_type(c_id) for c_id in
            feature.children.values_list('pk', flat=True)]
        feature_content = OrderedDict((
            ('id', text_type(feature_id)),
            ('slug', feature.slug),
            ('mdn_uri', feature.mdn_uri or None),
            ('experimental', feature.experimental),
            ('standardized', feature.standardized),
            ('stable', feature.stable),
            ('obsolete', feature.obsolete),
            ('name', feature.name),
            ('links', OrderedDict((
                ('sections', section_ids),
                ('supports', support_ids),
                ('parent', parent_id),
                ('children', children_ids))))))
        if list(feature.name.keys()) == ['zxx']:
            feature_content['name'] = feature.name['zxx']
        return feature_content

    def new_feature(self, feature_entry):
        """Serialize a new feature."""
        if feature_entry.get('canonical'):
            fname = feature_entry['name']
        else:
            fname = {'en': feature_entry['name']}
        feature_content = OrderedDict((
            ('id', feature_entry['id']),
            ('slug', feature_entry['slug']),
            ('mdn_uri', None),
            ('experimental', feature_entry.get('experimental', False)),
            ('standardized', feature_entry.get('standardized', True)),
            ('stable', feature_entry.get('stable', True)),
            ('obsolete', feature_entry.get('obsolete', False)),
            ('name', fname),
            ('links', OrderedDict((
                ('sections', []),
                ('supports', []),
                ('parent', text_type(self.feature.id)),
                ('children', []))))))
        return feature_content

    def load_version(self, version_id):
        """Serialize an existing version."""
        version = Version.objects.get(id=version_id)
        version_content = OrderedDict((
            ('id', text_type(version.id)),
            ('version', version.version or None),
            ('release_day', date_to_iso(version.release_day)),
            ('retirement_day', date_to_iso(version.retirement_day)),
            ('status', version.status),
            ('release_notes_uri', version.release_notes_uri or None),
            ('note', version.note or None),
            ('order', version._order),
            ('links', OrderedDict((
                ('browser', text_type(version.browser_id)),)))))
        return version_content

    def new_version(self, version_entry):
        """Serialize a new version."""
        version = version_entry['version']
        status = 'unknown'
        if version == 'nightly':
            status = 'future'
        elif not version:
            version = 'current'
            status = 'current'
        version_content = OrderedDict((
            ('id', version_entry['id']),
            ('version', version),
            ('release_day', None),
            ('retirement_day', None),
            ('status', status),
            ('release_notes_uri', None),
            ('note', None),
            ('links', OrderedDict((
                ('browser', text_type(version_entry['browser'])),)))))
        return version_content

    def load_support(self, support_id):
        """Serialize an existing support."""
        support = Support.objects.get(id=support_id)
        support_content = OrderedDict((
            ('id', text_type(support.id)),
            ('support', support.support),
            ('prefix', support.prefix or None),
            ('prefix_mandatory', support.prefix_mandatory),
            ('alternate_name', support.alternate_name or None),
            ('alternate_mandatory', support.alternate_mandatory),
            ('requires_config', support.requires_config or None),
            ('default_config', support.default_config or None),
            ('protected', support.protected),
            ('note', support.note or None),
            ('links', OrderedDict((
                ('version', text_type(support.version_id)),
                ('feature', text_type(support.feature_id)))))))
        return support_content

    def new_support(self, support_entry):
        """Serialize a new support."""
        support_content = OrderedDict((
            ('id', support_entry['id']),
            ('support', support_entry['support']),
            ('prefix', support_entry.get('prefix')),
            ('prefix_mandatory', bool(support_entry.get('prefix', False))),
            ('alternate_name', support_entry.get('alternate_name')),
            ('alternate_mandatory',
                support_entry.get('alternate_mandatory', False)),
            ('requires_config', support_entry.get('requires_config')),
            ('default_config', support_entry.get('default_config')),
            ('protected', support_entry.get('protected', False)),
            ('note', None),
            ('links', OrderedDict((
                ('version', text_type(support_entry['version'])),
                ('feature', text_type(support_entry['feature'])))))))
        if support_entry.get('footnote'):
            support_content['note'] = {'en': support_entry['footnote']}
        return support_content


def scrape_feature_page(feature_page):
    """Scrape a FeaturePage object"""
    en_content = feature_page.translatedcontent_set.get(locale='en-US')
    scraped_data = scrape_page(en_content.raw, feature_page.feature)
    view_feature = ScrapedViewFeature(feature_page, scraped_data)
    merged_data = view_feature.generate_data()

    # Add issues
    for issue in scraped_data['issues']:
        feature_page.add_issue(issue, 'en-US')
    merged_data['meta']['scrape']['issues'] = (
        feature_page.data['meta']['scrape']['issues'])

    # Update status, issues
    has_data = (scraped_data['specs'] or scraped_data['compat'] or
                scraped_data['issues'])
    if has_data:
        feature_page.status = feature_page.STATUS_PARSED
    else:
        feature_page.status = feature_page.STATUS_NO_DATA
    merged_data['meta']['scrape']['phase'] = feature_page.get_status_display()
    feature_page.data = merged_data
    feature_page.save()


#
# Utility methods
#
def date_to_iso(date):
    """Convert a datetime.Date to the ISO 8601 format, or None"""
    if date:
        return date.isoformat()
    else:
        return None


def end_of_line(text, pos):
    """Get the position of the end of the line from pos"""
    try:
        return text.index('\n', pos)
    except ValueError:
        return len(text)
