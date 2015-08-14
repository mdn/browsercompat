# coding: utf-8
"""Parser for HTML fragments used on MDN.

This is designed to be a foundation for more specific tasks, such as
extracting compatibility data from MDN pages, or validating API data when
an HTML subset is allowed.

HTML is actually unparsable, according to smart people:
http://trevorjim.com/a-grammar-for-html5/

So, this code is incomplete and impossible and possibly unreviewable.
"""
from __future__ import unicode_literals

from collections import OrderedDict
import re

from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type, string_types

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from .utils import join_content
from .visitor import Visitor

# Parsimonious grammar for HTML fragments
html_grammar_source = r"""
#
# HTML tokens (only those used in compat tables)
#
html = html_block / empty_text
html_block = html_element+
html_element = a_element /
    abbr_element /
    acronym_element /
    annotation_element /
    b_element /
    blockquote_element /
    br_element /
    caption_element /
    cite_element /
    code_element /
    dd_element /
    del_element /
    details_element /
    dfn_element /
    div_element /
    dl_element /
    dt_element /
    em_element /
    figcaption_element /
    figure_element /
    font_element /
    h1_element / h2_element / h3_element / h3_element / h4_element /
    h5_element / h6_element /
    hr_element /
    i_element /
    img_element /
    ins_element /
    input_element /
    kbd_element /
    label_element /
    li_element /
    mark_element /
    math_element /
    menclose_element /
    mfenced_element /
    mfrac_element /
    mi_element /
    mmultiscripts_element /
    mn_element /
    mo_element /
    mover_element /
    mphantom_element /
    mprescripts_element /
    mroot_element /
    mrow_element /
    ms_element /
    mspace_element /
    msqrt_element /
    mstyle_element /
    msub_element /
    msubsup_element /
    msup_element /
    mtable_element /
    mtd_element /
    mtext_element /
    mtr_element /
    munder_element /
    munderover_element /
    nobr_element /
    none_element /
    ol_element /
    option_element /
    p_element /
    pre_element /
    q_element /
    s_element /
    samp_element /
    section_element /
    select_element /
    semantics_element /
    small_element /
    span_element /
    strong_element /
    sub_element /
    sup_element /
    table_element /
    tbody_element /
    td_element /
    th_element /
    thead_element /
    tr_element /
    u_element /
    ul_element /
    var_element /
    text_block

a_element = a_open a_content a_close
a_open = "<a" _ attrs ">"
a_content = html
a_close = "</a>"

abbr_element = abbr_open abbr_content abbr_close
abbr_open = "<abbr" _ attrs ">"
abbr_content = html
abbr_close = "</abbr>"

acronym_element = acronym_open acronym_content acronym_close
acronym_open = "<acronym" _ attrs ">"
acronym_content = html
acronym_close = "</acronym>"

annotation_element = annotation_open annotation_content annotation_close
annotation_open = "<annotation" _ attrs ">"
annotation_content = html
annotation_close = "</annotation>"

b_element = b_open b_content b_close
b_open = "<b" _ attrs ">"
b_content = html
b_close = "</b>"

blockquote_element = blockquote_open blockquote_content blockquote_close
blockquote_open = "<blockquote" _ attrs ">"
blockquote_content = html
blockquote_close = "</blockquote>"

br_element = "<br" _ attrs ("/>" / ">")

caption_element = caption_open caption_content caption_close
caption_open = "<caption" _ attrs ">"
caption_content = html
caption_close = "</caption>"

cite_element = cite_open cite_content cite_close
cite_open = "<cite" _ attrs ">"
cite_content = html
cite_close = "</cite>"

code_element = code_open code_content code_close
code_open = "<code" _ attrs ">"
code_content = ~r"(?P<content>.*?(?=</code>))"s
code_close = "</code>"

dd_element = dd_open dd_content dd_close
dd_open = "<dd" _ attrs ">"
dd_content = html
dd_close = "</dd>"

del_element = del_open del_content del_close
del_open = "<del" _ attrs ">"
del_content = html
del_close = "</del>"

details_element = details_open details_content details_close
details_open = "<details" _ attrs ">"
details_content = html
details_close = "</details>"

dfn_element = dfn_open dfn_content dfn_close
dfn_open = "<dfn" _ attrs ">"
dfn_content = html
dfn_close = "</dfn>"

div_element = div_open div_content div_close
div_open = "<div" _ attrs ">"
div_content = html
div_close = "</div>"

dl_element = dl_open dl_content dl_close
dl_open = "<dl" _ attrs ">"
dl_content = html
dl_close = "</dl>"

dt_element = dt_open dt_content dt_close
dt_open = "<dt" _ attrs ">"
dt_content = html
dt_close = "</dt>"

em_element = em_open em_content em_close
em_open = "<em" _ attrs ">"
em_content = html
em_close = "</em>"

figcaption_element = figcaption_open figcaption_content figcaption_close
figcaption_open = "<figcaption" _ attrs ">"
figcaption_content = html
figcaption_close = "</figcaption>"

figure_element = figure_open figure_content figure_close
figure_open = "<figure" _ attrs ">"
figure_content = html
figure_close = "</figure>"

font_element = font_open font_content font_close
font_open = "<font" _ attrs ">"
font_content = html
font_close = "</font>"

h1_element = h1_open h1_content h1_close
h1_open = "<h1" _ attrs ">"
h1_content = html
h1_close = "</h1>"

h2_element = h2_open h2_content h2_close
h2_open = "<h2" _ attrs ">"
h2_content = html
h2_close = "</h2>"

h3_element = h3_open h3_content h3_close
h3_open = "<h3" _ attrs ">"
h3_content = html
h3_close = "</h3>"

h4_element = h4_open h4_content h4_close
h4_open = "<h4" _ attrs ">"
h4_content = html
h4_close = "</h4>"

h5_element = h5_open h5_content h5_close
h5_open = "<h5" _ attrs ">"
h5_content = html
h5_close = "</h5>"

h6_element = h6_open h6_content h6_close
h6_open = "<h6" _ attrs ">"
h6_content = html
h6_close = "</h6>"

hr_element = "<hr" _ attrs ("/>" / ">")

i_element = i_open i_content i_close
i_open = "<i" _ attrs ">"
i_content = html
i_close = "</i>"

img_element = "<img" _ attrs ("/>" / ">")

input_element = "<input" _ attrs ("/>" / ">")

ins_element = ins_open ins_content ins_close
ins_open = "<ins" _ attrs ">"
ins_content = html
ins_close = "</ins>"

kbd_element = kbd_open kbd_content kbd_close
kbd_open = "<kbd" _ attrs ">"
kbd_content = html
kbd_close = "</kbd>"

label_element = label_open label_content label_close
label_open = "<label" _ attrs ">"
label_content = html
label_close = "</label>"

li_element = li_open li_content li_close
li_open = "<li" _ attrs ">"
li_content = html
li_close = "</li>"

mark_element = mark_open mark_content mark_close
mark_open = "<mark" _ attrs ">"
mark_content = html
mark_close = "</mark>"

math_element = math_open math_content math_close
math_open = "<math" _ attrs ">"
math_content = html
math_close = "</math>"

menclose_element = menclose_open menclose_content menclose_close
menclose_open = "<menclose" _ attrs ">"
menclose_content = html
menclose_close = "</menclose>"

mfenced_element = mfenced_open mfenced_content mfenced_close
mfenced_open = "<mfenced" _ attrs ">"
mfenced_content = html
mfenced_close = "</mfenced>"

mfrac_element = mfrac_open mfrac_content mfrac_close
mfrac_open = "<mfrac" _ attrs ">"
mfrac_content = html
mfrac_close = "</mfrac>"

mi_element = mi_open mi_content mi_close
mi_open = "<mi" _ attrs ">"
mi_content = html
mi_close = "</mi>"

mmultiscripts_element = mmultiscripts_open mmultiscripts_content
    mmultiscripts_close
mmultiscripts_open = "<mmultiscripts" _ attrs ">"
mmultiscripts_content = html
mmultiscripts_close = "</mmultiscripts>"

mn_element = mn_open mn_content mn_close
mn_open = "<mn" _ attrs ">"
mn_content = html
mn_close = "</mn>"

mo_element = mo_open mo_content mo_close
mo_open = "<mo" _ attrs ">"
mo_content = html
mo_close = "</mo>"

mover_element = mover_open mover_content mover_close
mover_open = "<mover" _ attrs ">"
mover_content = html
mover_close = "</mover>"

mphantom_element = mphantom_open mphantom_content mphantom_close
mphantom_open = "<mphantom" _ attrs ">"
mphantom_content = html
mphantom_close = "</mphantom>"

mprescripts_element = mprescripts_open mprescripts_content mprescripts_close
mprescripts_open = "<mprescripts" _ attrs ">"
mprescripts_content = html
mprescripts_close = "</mprescripts>"

mroot_element = mroot_open mroot_content mroot_close
mroot_open = "<mroot" _ attrs ">"
mroot_content = html
mroot_close = "</mroot>"

mrow_element = mrow_open mrow_content mrow_close
mrow_open = "<mrow" _ attrs ">"
mrow_content = html
mrow_close = "</mrow>"

ms_element = ms_open ms_content ms_close
ms_open = "<ms" _ attrs ">"
ms_content = html
ms_close = "</ms>"

mspace_element = mspace_open mspace_content mspace_close
mspace_open = "<mspace" _ attrs ">"
mspace_content = html
mspace_close = "</mspace>"

msqrt_element = msqrt_open msqrt_content msqrt_close
msqrt_open = "<msqrt" _ attrs ">"
msqrt_content = html
msqrt_close = "</msqrt>"

mstyle_element = mstyle_open mstyle_content mstyle_close
mstyle_open = "<mstyle" _ attrs ">"
mstyle_content = html
mstyle_close = "</mstyle>"

msub_element = msub_open msub_content msub_close
msub_open = "<msub" _ attrs ">"
msub_content = html
msub_close = "</msub>"

msubsup_element = msubsup_open msubsup_content msubsup_close
msubsup_open = "<msubsup" _ attrs ">"
msubsup_content = html
msubsup_close = "</msubsup>"

msup_element = msup_open msup_content msup_close
msup_open = "<msup" _ attrs ">"
msup_content = html
msup_close = "</msup>"

mtable_element = mtable_open mtable_content mtable_close
mtable_open = "<mtable" _ attrs ">"
mtable_content = html
mtable_close = "</mtable>"

mtd_element = mtd_open mtd_content mtd_close
mtd_open = "<mtd" _ attrs ">"
mtd_content = html
mtd_close = "</mtd>"

mtext_element = mtext_open mtext_content mtext_close
mtext_open = "<mtext" _ attrs ">"
mtext_content = html
mtext_close = "</mtext>"

mtr_element = mtr_open mtr_content mtr_close
mtr_open = "<mtr" _ attrs ">"
mtr_content = html
mtr_close = "</mtr>"

munder_element = munder_open munder_content munder_close
munder_open = "<munder" _ attrs ">"
munder_content = html
munder_close = "</munder>"

munderover_element = munderover_open munderover_content munderover_close
munderover_open = "<munderover" _ attrs ">"
munderover_content = html
munderover_close = "</munderover>"

nobr_element = nobr_open nobr_content nobr_close
nobr_open = "<nobr" _ attrs ">"
nobr_content = html
nobr_close = "</nobr>"

none_element = none_open none_content none_close
none_open = "<none" _ attrs ">"
none_content = html
none_close = "</none>"

ol_element = ol_open ol_content ol_close
ol_open = "<ol" _ attrs ">"
ol_content = html
ol_close = "</ol>"

option_element = option_open option_content option_close
option_open = "<option" _ attrs ">"
option_content = html
option_close = "</option>"

p_element = p_open p_content p_close
p_open = "<p" _ attrs ">"
p_content = html
p_close = "</p>"

pre_element = pre_open pre_content pre_close
pre_open = "<pre" _ attrs ">"
pre_content = ~r"(?P<content>.*?(?=</pre>))"s
pre_close = "</pre>"

q_element = q_open q_content q_close
q_open = "<q" _ attrs ">"
q_content = html
q_close = "</q>"

s_element = s_open s_content s_close
s_open = "<s" _ attrs ">"
s_content = html
s_close = "</s>"

samp_element = samp_open samp_content samp_close
samp_open = "<samp" _ attrs ">"
samp_content = html
samp_close = "</samp>"

section_element = section_open section_content section_close
section_open = "<section" _ attrs ">"
section_content = html
section_close = "</section>"

select_element = select_open select_content select_close
select_open = "<select" _ attrs ">"
select_content = html
select_close = "</select>"

semantics_element = semantics_open semantics_content semantics_close
semantics_open = "<semantics" _ attrs ">"
semantics_content = html
semantics_close = "</semantics>"

small_element = small_open small_content small_close
small_open = "<small" _ attrs ">"
small_content = html
small_close = "</small>"

span_element = span_open span_content span_close
span_open = "<span" _ attrs ">"
span_content = html
span_close = "</span>"

strong_element = strong_open strong_content strong_close
strong_open = "<strong" _ attrs ">"
strong_content = html
strong_close = "</strong>"

sub_element = sub_open sub_content sub_close
sub_open = "<sub" _ attrs ">"
sub_close = "</sub>"
sub_content = html

sup_element = sup_open sup_content sup_close
sup_open = "<sup" _ attrs ">"
sup_close = "</sup>"
sup_content = html

table_element = table_open table_content table_close
table_open = "<table" _ attrs ">"
table_content = html
table_close = "</table>"

tbody_element = tbody_open tbody_content tbody_close
tbody_open = "<tbody" _ attrs ">"
tbody_content = html
tbody_close = "</tbody>"

td_element = td_open td_content td_close
td_open = "<td" _ attrs ">"
td_content = html
td_close = "</td>"

th_element = th_open th_content th_close
th_open = "<th" _ attrs ">"
th_content = html
th_close = "</th>"

thead_element = thead_open thead_content thead_close
thead_open = "<thead" _ attrs ">"
thead_content = html
thead_close = "</thead>"

tr_element = tr_open tr_content tr_close
tr_open = "<tr" _ attrs ">"
tr_content = html
tr_close = "</tr>"

u_element = u_open u_content u_close
u_open = "<u" _ attrs ">"
u_content = html
u_close = "</u>"

ul_element = ul_open ul_content ul_close
ul_open = "<ul" _ attrs ">"
ul_content = html
ul_close = "</ul>"

var_element = var_open var_content var_close
var_open = "<var" _ attrs ">"
var_content = html
var_close = "</var>"

#
# HTML tag attributes
#
attrs = attr*
attr = _ (assign_attr / ident) _
assign_attr = ident _ "=" _ value
ident = ~r"(?P<content>[a-z][a-z0-9-:]*)"
value = (double_quoted_text / single_quoted_text / "0" / "1")

#
# Generic text
#
text = (double_quoted_text / single_quoted_text / bare_text)
bare_text = ~r"(?P<content>[^<]*)"
double_quoted_text = ~r'"(?P<content>(?:[^"\\]|\\.)*)"'
single_quoted_text = ~r"'(?P<content>(?:[^'\\]|\\.)*)'"
# Whitespace
_ = ~r"[ \t\r\n]*"s

#
# Text segments
# Derived grammars can redefine text_token and text_item
#
text_block = text_token+
text_token = text_item
text_item = ~r"(?P<content>[^<]+)"s
empty_text = ""
"""
html_grammar = Grammar(html_grammar_source)


@python_2_unicode_compatible
class HTMLInterval(object):
    """A span of HTML content, from a tag to text."""

    def __init__(self, raw='', start=0):
        self.raw = raw
        self.start = start

    @property
    def end(self):
        return self.start + len(self.raw)

    def __str__(self):
        return self.raw

    def to_html(self):
        """Convert to HTML."""
        return text_type(self)

    def to_text(self):
        """Convert to non-HTML text."""
        return ""

    @property
    def issues(self):
        return []


@python_2_unicode_compatible
class HTMLText(HTMLInterval):
    """A plain text section of HTML"""

    def __init__(self, **kwargs):
        super(HTMLText, self).__init__(**kwargs)
        self.cleaned = self.cleanup_whitespace(self.raw)

    def __str__(self):
        return self.cleaned

    re_whitespace = re.compile(r'''(?x)  # Be verbose
    (\s|                # Any whitespace, or
     (<\s*br\s*/?>)|    # A variant of <br>, or
     \xa0|              # Unicode non-breaking space, or
     (\&nbsp;)          # HTML nbsp character
    )+                  # One or more in a row
    ''')

    def to_text(self):
        return self.cleaned

    def cleanup_whitespace(self, text):
        """Normalize whitespace"""
        normal = self.re_whitespace.sub(' ', text)
        assert '  ' not in normal
        return normal.strip()


@python_2_unicode_compatible
class HTMLEmptyText(HTMLText):
    """An empty text section of HTML"""

    def __init__(self, **kwargs):
        super(HTMLEmptyText, self).__init__(**kwargs)
        assert self.raw == ''

    def __str__(self):
        return ''


@python_2_unicode_compatible
class HTMLBaseTag(HTMLInterval):
    """An HTML tag, such as <li>, <br/>, or </code>"""

    def __init__(self, tag, **kwargs):
        super(HTMLBaseTag, self).__init__(**kwargs)
        assert tag in self.raw
        self.tag = tag

    def __str__(self):
        return "<{}>".format(self.tag)


@python_2_unicode_compatible
class HTMLAttribute(HTMLInterval):
    """An attribute of an HTML tag."""

    def __init__(self, ident, value, **kwargs):
        super(HTMLAttribute, self).__init__(**kwargs)
        assert ident in self.raw
        if value is True:
            assert '=' not in self.raw
        elif value is False:
            raise ValueError('False is not an allowed value')
        else:
            assert text_type(value) in self.raw
        self.ident = ident
        self.value = value

    def __str__(self):
        if self.value is True:
            return self.ident
        if isinstance(self.value, string_types):
            fmt = '{}="{}"'
        else:
            fmt = '{}={}'
        return fmt.format(self.ident, self.value)


@python_2_unicode_compatible
class HTMLAttributes(HTMLInterval):
    """A collection of attributes."""

    def __init__(self, attributes=None, **kwargs):
        super(HTMLAttributes, self).__init__(**kwargs)
        self.attrs = OrderedDict()
        for attr in attributes or []:
            self.attrs[attr.ident] = attr

    def __str__(self):
        return ' '.join([str(attr) for attr in self.attrs.values()])

    def as_dict(self):
        return OrderedDict((k, v.value) for k, v in self.attrs.items())


@python_2_unicode_compatible
class HTMLOpenTag(HTMLBaseTag):
    """An HTML tag, such as <a href="#foo">"""

    def __init__(
            self, attributes, attribute_actions=None, drop_tag=False,
            scope=None, **kwargs):
        """Initialize an HTML open tag

        Keyword Arguments:
        attributes - An HTMLAttributes instance
        attribute_actions - A optional dictionary of attribute identifiers to
            validation actions (see validate_attributes).
        drop_tag - If true, the containing tag will be dropped in to_html()
        scope - The scope for issues
        """
        super(HTMLOpenTag, self).__init__(**kwargs)
        self.attributes = attributes
        self.drop_tag = drop_tag
        self.scope = scope

        if self.drop_tag:
            self._issues = (
                ('tag_dropped', self.start, self.end,
                 {'scope': self.scope, 'tag': self.tag}),)
        elif attribute_actions:
            self._issues = self.validate_attributes(
                attributes, attribute_actions)
        else:
            self._issues = []

    def __str__(self):
        attrs = str(self.attributes)
        if attrs:
            return '<{} {}>'.format(self.tag, attrs)
        else:
            return '<{}>'.format(self.tag)

    def validate_attributes(self, attributes, actions):
        """Validate attributes for an open tag.

        Attribute validation is controlled by actions, which is a
        dictionary of attribute identifiers ('class', 'href', etc.) to
        validation strategies.  The None identifier entry gives a default
        validation.

        Valid validation actions are:
        - 'ban': Drop the attribute, and add unexpected_attribute issue
        - 'drop': Drop the attribute
        - 'keep': Keep the attribute
        - 'must': Add missing_attribute issue if not present

        Return is a list of issues found in the attributes
        """
        # Verify attribute actions
        assert None in actions
        assert actions[None] in ('ban', 'drop', 'keep')

        # Are all actions 'keep' actions? Do nothing.
        if all([action == 'keep' for action in actions.values()]):
            return []

        # Look for missing 'must' attributes
        must_idents = set(
            ident for ident, action in actions.items() if action == 'must')
        has_idents = set(attributes.attrs.keys())
        missing_idents = must_idents - has_idents

        # Look for attributes to drop
        drop_idents = []
        for attr in attributes.attrs.values():
            ident = attr.ident
            action = actions.get(ident, actions[None])
            assert action in ('ban', 'drop', 'keep', 'must')
            if action in ('ban', 'drop'):
                drop_idents.append((ident, action))

        # Construct the expected attributes string
        if drop_idents:
            expected = sorted(must_idents)
            if len(expected) > 1:
                expected_text = (
                    'the attributes ' + ', '.join(expected[:-1]) + ' or ' +
                    expected[-1])
            elif len(expected) == 1:
                expected_text = 'the attribute ' + expected[0]
            else:
                expected_text = 'no attributes'

        # Drop attributes, and add issues for banned attributes
        issues = []
        for ident, action in drop_idents:
            if action == 'ban':
                attr = attributes.attrs[ident]
                issues.append((
                    'unexpected_attribute', attr.start, attr.end,
                    {'node_type': self.tag, 'ident': ident,
                     'value': attr.value, 'expected': expected_text}))
            del attributes.attrs[ident]

        # Add issues for missing required attributes
        for ident in missing_idents:
            issues.append((
                'missing_attribute', self.start, self.end,
                {'node_type': self.tag, 'ident': ident}))

        return issues

    @property
    def issues(self):
        return self._issues


@python_2_unicode_compatible
class HTMLCloseTag(HTMLBaseTag):
    """An HTML closing tag, such as </a>"""
    pass

    def __str__(self):
        return "</{}>".format(self.tag)


class HTMLSelfClosingElement(HTMLOpenTag):
    """An HTML element that is just a tag, such as <br> and <img>."""

    def to_html(self):
        if self.drop_tag:
            return ""
        else:
            return super(HTMLSelfClosingElement, self).to_html()


@python_2_unicode_compatible
class HTMLElement(HTMLInterval):
    """An HTML element that contains child elements"""

    def __init__(
            self, open_tag, close_tag=None, children=None, drop_tag=False,
            scope=None, **kwargs):
        super(HTMLElement, self).__init__(**kwargs)
        self.open_tag = open_tag
        self.close_tag = close_tag
        assert self.open_tag.tag == self.close_tag.tag
        self.tag = self.open_tag.tag
        self.children = []
        for child in (children or []):
            self.children.append(child)
        self.drop_tag = drop_tag

    def __str__(self):
        content = join_content(text_type(child) for child in self.children)
        return "{}{}{}".format(self.open_tag, content, self.close_tag)

    @cached_property
    def attributes(self):
        return self.open_tag.attributes.as_dict()

    def to_html(self, drop_tag=None):
        content = join_content(child.to_html() for child in self.children)
        if drop_tag is None:
            drop_tag = self.drop_tag
        if drop_tag:
            return content
        else:
            return "{}{}{}".format(self.open_tag, content, self.close_tag)

    def to_text(self):
        content = join_content(child.to_text() for child in self.children)
        return content


class HnElement(HTMLElement):
    """An HTML header, such as <h2>"""
    def __init__(self, **kwargs):
        super(HnElement, self).__init__(**kwargs)
        self.level = int(self.tag[1:])


class HTMLVisitor(Visitor):
    """Extract HTML structure from an HTML fragment.

    Handles the limited HTML structure allowed by the parser. If the HTML
    fragment is inside of a document, then an offset can be applied so that
    positions are reported relative to the whole document.
    """
    _default_attribute_actions = {None: 'keep'}
    _allowed_tags = None
    scope = 'HTML'

    def process(self, cls, node, **kwargs):
        """Convert a node to an HTML* instance"""
        dropable = issubclass(cls, (HTMLElement, HTMLOpenTag))
        if dropable and self._allowed_tags is not None:
            if issubclass(cls, HTMLOpenTag):
                if kwargs['tag'] not in self._allowed_tags:
                    kwargs['drop_tag'] = True
            else:
                if kwargs['open_tag'].tag not in self._allowed_tags:
                    kwargs['drop_tag'] = True
        processed = cls(
            raw=node.text, start=node.start + self.offset, **kwargs)
        for issue in processed.issues:
            self.add_raw_issue(issue)
        return processed

    #
    # Basic visitors
    #
    def generic_visit(self, node, visited_children):
        """Visitor when none is specified."""
        return visited_children or node

    def _visit_content(self, node, children):
        """Visitor for re nodes with a named (?P<content>) section."""
        return node.match.group('content')

    def _visit_block(self, node, tokens):
        """Visit a 1-or-more block of tokens."""
        assert isinstance(tokens, list)
        for token in tokens:
            assert isinstance(token, HTMLInterval)
        return tokens

    def _visit_token(self, node, children):
        """Visit a single (possibly list-wrapped) token."""
        assert len(children) == 1
        item = children[0]
        if isinstance(item, HTMLInterval):
            return item
        else:
            assert len(item) == 1, item
            assert isinstance(item[0], HTMLInterval), item[0]
            return item[0]

    #
    # HTML tokens
    #
    def visit_html(self, node, children):
        assert isinstance(children, list)
        assert len(children) == 1
        return children[0]

    visit_html_block = _visit_block
    visit_html_element = _visit_token
    visit_hn_element = _visit_token

    def _visit_open(self, node, children, actions=None, cls=None, **kwargs):
        """Parse an opening tag with an optional attributes list"""
        open_tag_node, ws, attrs, close = children
        assert isinstance(open_tag_node, Node), type(open_tag_node)
        open_tag = open_tag_node.text
        assert open_tag.startswith('<')
        tag = open_tag[1:]
        assert isinstance(attrs, HTMLAttributes), type(attrs)
        cls = cls or HTMLOpenTag
        return self.process(
            cls, node, tag=tag, attributes=attrs, scope=self.scope,
            attribute_actions=actions or self._default_attribute_actions,
            **kwargs)

    visit_a_open = _visit_open
    visit_acronym_open = _visit_open
    visit_annotation_open = _visit_open
    visit_abbr_open = _visit_open
    visit_b_open = _visit_open
    visit_blockquote_open = _visit_open
    visit_caption_open = _visit_open
    visit_cite_open = _visit_open
    visit_code_open = _visit_open
    visit_dd_open = _visit_open
    visit_del_open = _visit_open
    visit_details_open = _visit_open
    visit_dfn_open = _visit_open
    visit_div_open = _visit_open
    visit_dl_open = _visit_open
    visit_dt_open = _visit_open
    visit_em_open = _visit_open
    visit_figcaption_open = _visit_open
    visit_figure_open = _visit_open
    visit_font_open = _visit_open
    visit_h1_open = _visit_open
    visit_h2_open = _visit_open
    visit_h3_open = _visit_open
    visit_h4_open = _visit_open
    visit_h5_open = _visit_open
    visit_h6_open = _visit_open
    visit_i_open = _visit_open
    visit_ins_open = _visit_open
    visit_label_open = _visit_open
    visit_li_open = _visit_open
    visit_kbd_open = _visit_open
    visit_mark_open = _visit_open
    visit_math_open = _visit_open
    visit_menclose_open = _visit_open
    visit_mfenced_open = _visit_open
    visit_mfrac_open = _visit_open
    visit_mi_open = _visit_open
    visit_mmultiscripts_open = _visit_open
    visit_mn_open = _visit_open
    visit_mo_open = _visit_open
    visit_mover_open = _visit_open
    visit_mphantom_open = _visit_open
    visit_mprescripts_open = _visit_open
    visit_mroot_open = _visit_open
    visit_mrow_open = _visit_open
    visit_ms_open = _visit_open
    visit_mspace_open = _visit_open
    visit_msqrt_open = _visit_open
    visit_mstyle_open = _visit_open
    visit_msub_open = _visit_open
    visit_msubsup_open = _visit_open
    visit_msup_open = _visit_open
    visit_mtable_open = _visit_open
    visit_mtd_open = _visit_open
    visit_mtext_open = _visit_open
    visit_mtr_open = _visit_open
    visit_munder_open = _visit_open
    visit_munderover_open = _visit_open
    visit_none_open = _visit_open
    visit_nobr_open = _visit_open
    visit_ol_open = _visit_open
    visit_option_open = _visit_open
    visit_p_open = _visit_open
    visit_pre_open = _visit_open
    visit_q_open = _visit_open
    visit_s_open = _visit_open
    visit_samp_open = _visit_open
    visit_section_open = _visit_open
    visit_select_open = _visit_open
    visit_semantics_open = _visit_open
    visit_small_open = _visit_open
    visit_span_open = _visit_open
    visit_strong_open = _visit_open
    visit_sub_open = _visit_open
    visit_sup_open = _visit_open
    visit_table_open = _visit_open
    visit_tbody_open = _visit_open
    visit_td_open = _visit_open
    visit_th_open = _visit_open
    visit_thead_open = _visit_open
    visit_tr_open = _visit_open
    visit_u_open = _visit_open
    visit_ul_open = _visit_open
    visit_var_open = _visit_open

    def _visit_self_closing_element(self, node, children, **kwargs):
        return self._visit_open(
            node, children, cls=HTMLSelfClosingElement, **kwargs)

    visit_br_element = _visit_self_closing_element
    visit_hr_element = _visit_self_closing_element
    visit_img_element = _visit_self_closing_element
    visit_input_element = _visit_self_closing_element

    def _visit_close(self, node, empty):
        close_tag = node.text
        assert close_tag.startswith('</')
        assert close_tag.endswith('>')
        tag = close_tag[2:-1]
        return self.process(HTMLCloseTag, node, tag=tag)

    visit_a_close = _visit_close
    visit_acronym_close = _visit_close
    visit_annotation_close = _visit_close
    visit_abbr_close = _visit_close
    visit_b_close = _visit_close
    visit_blockquote_close = _visit_close
    visit_caption_close = _visit_close
    visit_cite_close = _visit_close
    visit_code_close = _visit_close
    visit_dd_close = _visit_close
    visit_del_close = _visit_close
    visit_details_close = _visit_close
    visit_dfn_close = _visit_close
    visit_div_close = _visit_close
    visit_dl_close = _visit_close
    visit_dt_close = _visit_close
    visit_em_close = _visit_close
    visit_figcaption_close = _visit_close
    visit_figure_close = _visit_close
    visit_font_close = _visit_close
    visit_h1_close = _visit_close
    visit_h2_close = _visit_close
    visit_h3_close = _visit_close
    visit_h4_close = _visit_close
    visit_h5_close = _visit_close
    visit_h6_close = _visit_close
    visit_i_close = _visit_close
    visit_ins_close = _visit_close
    visit_label_close = _visit_close
    visit_li_close = _visit_close
    visit_kbd_close = _visit_close
    visit_mark_close = _visit_close
    visit_math_close = _visit_close
    visit_menclose_close = _visit_close
    visit_mfenced_close = _visit_close
    visit_mfrac_close = _visit_close
    visit_mi_close = _visit_close
    visit_mmultiscripts_close = _visit_close
    visit_mn_close = _visit_close
    visit_mo_close = _visit_close
    visit_mover_close = _visit_close
    visit_mphantom_close = _visit_close
    visit_mprescripts_close = _visit_close
    visit_mroot_close = _visit_close
    visit_mrow_close = _visit_close
    visit_ms_close = _visit_close
    visit_mspace_close = _visit_close
    visit_msqrt_close = _visit_close
    visit_mstyle_close = _visit_close
    visit_msub_close = _visit_close
    visit_msubsup_close = _visit_close
    visit_msup_close = _visit_close
    visit_mtable_close = _visit_close
    visit_mtd_close = _visit_close
    visit_mtext_close = _visit_close
    visit_mtr_close = _visit_close
    visit_munder_close = _visit_close
    visit_munderover_close = _visit_close
    visit_nobr_close = _visit_close
    visit_none_close = _visit_close
    visit_ol_close = _visit_close
    visit_option_close = _visit_close
    visit_p_close = _visit_close
    visit_pre_close = _visit_close
    visit_q_close = _visit_close
    visit_s_close = _visit_close
    visit_samp_close = _visit_close
    visit_section_close = _visit_close
    visit_select_close = _visit_close
    visit_semantics_close = _visit_close
    visit_small_close = _visit_close
    visit_span_close = _visit_close
    visit_strong_close = _visit_close
    visit_sub_close = _visit_close
    visit_sup_close = _visit_close
    visit_table_close = _visit_close
    visit_tbody_close = _visit_close
    visit_td_close = _visit_close
    visit_th_close = _visit_close
    visit_thead_close = _visit_close
    visit_tr_close = _visit_close
    visit_u_close = _visit_close
    visit_ul_close = _visit_close
    visit_var_close = _visit_close

    def _visit_element(self, node, children, **kwargs):
        """Parse a <tag>content</tag> element."""
        open_tag, content, close_tag = children
        assert isinstance(open_tag, HTMLOpenTag), type(open_tag)
        if isinstance(content, (HTMLText, HTMLEmptyText)):
            children = [content]
        else:
            assert isinstance(content, list), type(content)
            for child in content:
                assert isinstance(child, HTMLInterval), child
            children = content
        assert isinstance(close_tag, HTMLCloseTag), type(close_tag)
        element_class = kwargs.pop('element_class', HTMLElement)
        return self.process(
            element_class, node, open_tag=open_tag, close_tag=close_tag,
            children=children, scope=self.scope, **kwargs)

    visit_a_element = _visit_element
    visit_acronym_element = _visit_element
    visit_annotation_element = _visit_element
    visit_abbr_element = _visit_element
    visit_b_element = _visit_element
    visit_blockquote_element = _visit_element
    visit_caption_element = _visit_element
    visit_cite_element = _visit_element
    visit_dd_element = _visit_element
    visit_del_element = _visit_element
    visit_details_element = _visit_element
    visit_dfn_element = _visit_element
    visit_div_element = _visit_element
    visit_dl_element = _visit_element
    visit_dt_element = _visit_element
    visit_em_element = _visit_element
    visit_figcaption_element = _visit_element
    visit_figure_element = _visit_element
    visit_font_element = _visit_element
    visit_i_element = _visit_element
    visit_ins_element = _visit_element
    visit_label_element = _visit_element
    visit_li_element = _visit_element
    visit_kbd_element = _visit_element
    visit_mark_element = _visit_element
    visit_math_element = _visit_element
    visit_menclose_element = _visit_element
    visit_mfenced_element = _visit_element
    visit_mfrac_element = _visit_element
    visit_mi_element = _visit_element
    visit_mmultiscripts_element = _visit_element
    visit_mn_element = _visit_element
    visit_mo_element = _visit_element
    visit_mover_element = _visit_element
    visit_mphantom_element = _visit_element
    visit_mprescripts_element = _visit_element
    visit_mroot_element = _visit_element
    visit_mrow_element = _visit_element
    visit_ms_element = _visit_element
    visit_mspace_element = _visit_element
    visit_msqrt_element = _visit_element
    visit_mstyle_element = _visit_element
    visit_msub_element = _visit_element
    visit_msubsup_element = _visit_element
    visit_msup_element = _visit_element
    visit_mtable_element = _visit_element
    visit_mtd_element = _visit_element
    visit_mtext_element = _visit_element
    visit_mtr_element = _visit_element
    visit_munder_element = _visit_element
    visit_munderover_element = _visit_element
    visit_nobr_element = _visit_element
    visit_none_element = _visit_element
    visit_ol_element = _visit_element
    visit_option_element = _visit_element
    visit_p_element = _visit_element
    visit_q_element = _visit_element
    visit_s_element = _visit_element
    visit_samp_element = _visit_element
    visit_section_element = _visit_element
    visit_select_element = _visit_element
    visit_semantics_element = _visit_element
    visit_small_element = _visit_element
    visit_span_element = _visit_element
    visit_strong_element = _visit_element
    visit_sub_element = _visit_element
    visit_sup_element = _visit_element
    visit_table_element = _visit_element
    visit_tbody_element = _visit_element
    visit_td_element = _visit_element
    visit_th_element = _visit_element
    visit_thead_element = _visit_element
    visit_tr_element = _visit_element
    visit_u_element = _visit_element
    visit_ul_element = _visit_element
    visit_var_element = _visit_element

    def _visit_text_element(self, node, children, **kwargs):
        """Parse a <tag>unparsed text</tag> element."""
        open_tag, content, close_tag = children
        assert isinstance(content, HTMLText)
        return self._visit_element(node, children, **kwargs)

    visit_code_element = _visit_text_element
    visit_pre_element = _visit_text_element

    def _visit_hn_element(self, node, children, **kwargs):
        return self._visit_element(
            node, children, element_class=HnElement, **kwargs)

    visit_h1_element = _visit_hn_element
    visit_h2_element = _visit_hn_element
    visit_h3_element = _visit_hn_element
    visit_h4_element = _visit_hn_element
    visit_h5_element = _visit_hn_element
    visit_h6_element = _visit_hn_element

    #
    # HTML tag attributes
    #
    def visit_attrs(self, node, attrs):
        """Parse an attribute list."""
        return self.process(HTMLAttributes, node, attributes=attrs)

    def visit_attr(self, node, children):
        """Strip whitespace from an attribute."""
        ws1, attr_option, ws2 = children
        assert len(attr_option) == 1
        attr = attr_option[0]
        if isinstance(attr, HTMLAttribute):
            return attr
        else:
            # Boolean attribute
            return self.process(HTMLAttribute, node, ident=attr, value=True)

    def visit_assign_attr(self, node, children):
        """Parse a single ident=value attribute."""
        ident, ws1, equals, ws2, value = children
        assert isinstance(ident, text_type), type(ident)
        assert isinstance(value, (text_type, int)), type(value)
        return self.process(HTMLAttribute, node, ident=ident, value=value)

    visit_ident = _visit_content

    def visit_value(self, node, valnode):
        value = valnode[0]
        if isinstance(value, text_type):
            return value
        else:
            return int(value.text)

    #
    # Generic text
    #
    visit_bare_text = _visit_content

    def _unslash_text(self, node, children):
        raw = self._visit_content(node, children)
        bits = []
        slash = False
        for char in raw:
            if char == '\\' and not slash:
                slash = True
            else:
                bits.append(char)
                slash = False
        return ''.join(bits)

    visit_single_quoted_text = _unslash_text
    visit_double_quoted_text = _unslash_text

    #
    # Text segments
    #

    visit_text_block = _visit_block
    visit_text_token = _visit_token

    def visit_text_item(self, node, empty):
        assert empty == []
        return self.process(HTMLText, node)

    visit_code_content = visit_text_item
    visit_pre_content = visit_text_item

    def visit_empty_text(self, node, empty):
        assert empty == []
        return self.process(HTMLEmptyText, node)
