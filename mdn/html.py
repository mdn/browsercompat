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

CONTAINER = 1
HEADER = 2
SELF_CLOSING = 3
RAW_CONTENT = 4

html_elements = OrderedDict((
    ('a', CONTAINER),
    ('abbr', CONTAINER),
    ('acronym', CONTAINER),
    ('annotation', CONTAINER),
    ('b', CONTAINER),
    ('blockquote', CONTAINER),
    ('br', SELF_CLOSING),
    ('caption', CONTAINER),
    ('cite', CONTAINER),
    ('code', RAW_CONTENT),
    ('dd', CONTAINER),
    ('del', CONTAINER),
    ('details', CONTAINER),
    ('dfn', CONTAINER),
    ('div', CONTAINER),
    ('dl', CONTAINER),
    ('dt', CONTAINER),
    ('em', CONTAINER),
    ('figcaption', CONTAINER),
    ('figure', CONTAINER),
    ('font', CONTAINER),
    ('h1', HEADER),
    ('h2', HEADER),
    ('h3', HEADER),
    ('h3', HEADER),
    ('h4', HEADER),
    ('h5', HEADER),
    ('h6', HEADER),
    ('hr', SELF_CLOSING),
    ('i', CONTAINER),
    ('img', SELF_CLOSING),
    ('input', SELF_CLOSING),
    ('ins', CONTAINER),
    ('kbd', CONTAINER),
    ('label', CONTAINER),
    ('li', CONTAINER),
    ('mark', CONTAINER),
    ('math', CONTAINER),
    ('menclose', CONTAINER),
    ('mfenced', CONTAINER),
    ('mfrac', CONTAINER),
    ('mi', CONTAINER),
    ('mmultiscripts', CONTAINER),
    ('mn', CONTAINER),
    ('mo', CONTAINER),
    ('mover', CONTAINER),
    ('mphantom', CONTAINER),
    ('mprescripts', CONTAINER),
    ('mroot', CONTAINER),
    ('mrow', CONTAINER),
    ('ms', CONTAINER),
    ('mspace', CONTAINER),
    ('msqrt', CONTAINER),
    ('mstyle', CONTAINER),
    ('msub', CONTAINER),
    ('msubsup', CONTAINER),
    ('msup', CONTAINER),
    ('mtable', CONTAINER),
    ('mtd', CONTAINER),
    ('mtext', CONTAINER),
    ('mtr', CONTAINER),
    ('munder', CONTAINER),
    ('munderover', CONTAINER),
    ('nobr', CONTAINER),
    ('none', CONTAINER),
    ('ol', CONTAINER),
    ('option', CONTAINER),
    ('p', CONTAINER),
    ('pre', RAW_CONTENT),
    ('q', CONTAINER),
    ('s', CONTAINER),
    ('samp', CONTAINER),
    ('section', CONTAINER),
    ('select', CONTAINER),
    ('semantics', CONTAINER),
    ('small', CONTAINER),
    ('span', CONTAINER),
    ('strong', CONTAINER),
    ('sub', CONTAINER),
    ('sup', CONTAINER),
    ('table', CONTAINER),
    ('tbody', CONTAINER),
    ('td', CONTAINER),
    ('th', CONTAINER),
    ('thead', CONTAINER),
    ('tfoot', CONTAINER),
    ('tr', CONTAINER),
    ('u', CONTAINER),
    ('ul', CONTAINER),
    ('var', CONTAINER),
))


# Parsimonious grammar for HTML fragments
def element_grammar(tag, element_type):
    """Return parsimonious grammar for an HTML element."""
    if element_type in (CONTAINER, HEADER):
        template = r"""
{tag}_element = {tag}_open {tag}_content {tag}_close
{tag}_open = "<{tag}" _ attrs ">"
{tag}_content = html
{tag}_close = "</{tag}>"
"""
    elif element_type == SELF_CLOSING:
        template = r"""
{tag}_element = "<{tag}" _ attrs ("/>" / ">")
"""
    else:
        assert element_type == RAW_CONTENT
        template = r"""
{tag}_element = {tag}_open {tag}_content {tag}_close
{tag}_open = "<{tag}" _ attrs ">"
{tag}_content = ~r"(?P<content>.*?(?=</{tag}>))"s
{tag}_close = "</{tag}>"
"""
    return template.format(tag=tag)

html_grammar_source = r"""
#
# HTML tokens (only those used in compat tables)
#
html = html_block / empty_text
html_block = html_element+
html_element = {html_element} / text_block
{html_elements}

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
""".format(
    html_element=' / '.join(tag + '_element' for tag in html_elements),
    html_elements=''.join(
        element_grammar(tag, element_type)
        for tag, element_type in html_elements.items()))
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
        return ''

    @property
    def issues(self):
        return []


@python_2_unicode_compatible
class HTMLText(HTMLInterval):
    """A plain text section of HTML."""

    def __init__(self, **kwargs):
        super(HTMLText, self).__init__(**kwargs)
        self.cleaned = self.cleanup_whitespace(self.raw)

    def __str__(self):
        return self.cleaned

    re_whitespace = re.compile(r'''(?x)  # Be verbose
    (\s|                # Any whitespace, or
     (<\s*br\s*/?>)|    # A variant of <br>, or
     \xa0|              # Unicode non-breaking space, or
     \ufeff|            # Unicode BOM
     (\&nbsp;)          # HTML nbsp character
    )+                  # One or more in a row
    ''')

    def to_text(self):
        return self.cleaned

    def cleanup_whitespace(self, text):
        """Normalize whitespace."""
        normal = self.re_whitespace.sub(' ', text)
        assert '  ' not in normal
        return normal.strip()


@python_2_unicode_compatible
class HTMLEmptyText(HTMLText):
    """An empty text section of HTML."""

    def __init__(self, **kwargs):
        super(HTMLEmptyText, self).__init__(**kwargs)
        assert self.raw == ''

    def __str__(self):
        return ''


@python_2_unicode_compatible
class HTMLBaseTag(HTMLInterval):
    """An HTML tag, such as <li>, <br/>, or </code>."""

    def __init__(self, tag, **kwargs):
        super(HTMLBaseTag, self).__init__(**kwargs)
        assert tag in self.raw
        self.tag = tag

    def __str__(self):
        return '<{}>'.format(self.tag)


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
    """An HTML tag, such as <a href="#foo">."""

    def __init__(
            self, attributes, attribute_actions=None, drop_tag=False,
            scope=None, **kwargs):
        """Initialize an HTML open tag.

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
    """An HTML closing tag, such as </a>."""

    def __str__(self):
        return '</{}>'.format(self.tag)


@python_2_unicode_compatible
class HTMLElement(HTMLInterval):
    """An HTML element that may contain child elements."""

    def __init__(
            self, open_tag, close_tag=None, children=None, drop_tag=False,
            scope=None, **kwargs):
        super(HTMLElement, self).__init__(**kwargs)
        self.open_tag = open_tag
        self.close_tag = close_tag
        if self.close_tag:
            assert self.open_tag.tag == self.close_tag.tag
        else:
            assert not children
        self.tag = self.open_tag.tag
        self.children = list(children or [])
        self.drop_tag = drop_tag

    def __str__(self):
        content = join_content(text_type(child) for child in self.children)
        if self.close_tag:
            return '{}{}{}'.format(self.open_tag, content, self.close_tag)
        else:
            return '{}'.format(self.open_tag)

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
            return text_type(self)

    def to_text(self):
        content = join_content(child.to_text() for child in self.children)
        return content


class HnElement(HTMLElement):
    """An HTML header, such as <h2>."""

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

    def __init__(self, **kwargs):
        super(HTMLVisitor, self).__init__(**kwargs)

    def process(self, cls, node, **kwargs):
        """Convert a node to an HTML* instance."""
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
        """Parse an opening tag with an optional attributes list."""
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

    def _visit_self_closing_element(self, node, children, **kwargs):
        open_tag = self._visit_open(node, children, **kwargs)
        return self.process(
            HTMLElement, node, open_tag=open_tag, scope=self.scope, **kwargs)

    def _visit_close(self, node, empty):
        close_tag = node.text
        assert close_tag.startswith('</')
        assert close_tag.endswith('>')
        tag = close_tag[2:-1]
        return self.process(HTMLCloseTag, node, tag=tag)

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

    def _visit_raw_element(self, node, children, **kwargs):
        """Parse a <tag>unparsed text</tag> element."""
        open_tag, content, close_tag = children
        assert isinstance(content, HTMLText)
        return self._visit_element(node, children, **kwargs)

    def _visit_hn_element(self, node, children, **kwargs):
        return self._visit_element(
            node, children, element_class=HnElement, **kwargs)

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

    def visit_empty_text(self, node, empty):
        assert empty == []
        return self.process(HTMLEmptyText, node)

# Add handlers for HTML elements
for tag, element_type in html_elements.items():
    name = 'visit_' + tag
    if element_type == CONTAINER:
        setattr(HTMLVisitor, name + '_open', HTMLVisitor._visit_open)
        setattr(HTMLVisitor, name + '_close', HTMLVisitor._visit_close)
        setattr(HTMLVisitor, name + '_element', HTMLVisitor._visit_element)
    elif element_type == HEADER:
        setattr(HTMLVisitor, name + '_open', HTMLVisitor._visit_open)
        setattr(HTMLVisitor, name + '_close', HTMLVisitor._visit_close)
        setattr(HTMLVisitor, name + '_element', HTMLVisitor._visit_hn_element)
    elif element_type == SELF_CLOSING:
        setattr(
            HTMLVisitor, name + '_element',
            HTMLVisitor._visit_self_closing_element)
    else:
        assert element_type == RAW_CONTENT
        setattr(HTMLVisitor, name + '_open', HTMLVisitor._visit_open)
        setattr(HTMLVisitor, name + '_close', HTMLVisitor._visit_close)
        setattr(HTMLVisitor, name + '_element', HTMLVisitor._visit_raw_element)
        setattr(HTMLVisitor, name + '_content', HTMLVisitor.visit_text_item)
