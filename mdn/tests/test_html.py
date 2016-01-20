# coding: utf-8
"""Test mdn.html."""
from __future__ import unicode_literals

from django.utils.six import text_type

from mdn.html import (
    HTMLAttribute, HTMLAttributes, HTMLCloseTag, HTMLElement, HTMLInterval,
    HTMLOpenTag, HTMLBaseTag, HTMLText, HTMLVisitor, HnElement, html_grammar)
from .base import TestCase


class TestHTMLInterval(TestCase):
    def test_str(self):
        interval = HTMLInterval(raw='Interval')
        self.assertEqual('Interval', text_type(interval))

    def test_to_html(self):
        interval = HTMLInterval(raw='Interval')
        self.assertEqual('Interval', interval.to_html())

    def test_to_text(self):
        interval = HTMLInterval(raw='Interval')
        self.assertEqual('', interval.to_text())


class TestHTMLText(TestCase):
    def test_str(self):
        text = HTMLText(raw='\nSome Text\n')
        self.assertEqual('Some Text', text_type(text))

    def test_to_text(self):
        text = HTMLText(raw='\nSome Text\n')
        self.assertEqual('Some Text', text.to_text())

    def test_bom_removed(self):
        text = HTMLText(raw='BOM -> \ufeff')
        self.assertEqual('BOM ->', text.to_text())


class TestHTMLBaseTag(TestCase):
    def test_str(self):
        tag = HTMLBaseTag(raw='<br/>', tag='br')
        self.assertEqual('<br>', text_type(tag))


class TestHTMLAttribute(TestCase):
    def test_str_string_value(self):
        attr = HTMLAttribute(
            raw='foo="bar"', ident='foo', value='bar')
        self.assertEqual('foo="bar"', text_type(attr))

    def test_str_int_value(self):
        attr = HTMLAttribute(raw='selected=1', ident='selected', value=1)
        self.assertEqual('selected=1', text_type(attr))

    def test_str_bool_value(self):
        attr = HTMLAttribute(
            raw='selected', ident='selected', value=True)
        self.assertEqual('selected', text_type(attr))

    def test_false_raises(self):
        self.assertRaises(
            ValueError, HTMLAttribute,
            raw='selected', ident='selected', value=False)


class TestHTMLAttributes(TestCase):
    def test_str_empty(self):
        attrs = HTMLAttributes(raw=' ')
        self.assertEqual('', text_type(attrs))

    def test_str_attrs(self):
        attr_text = 'href="http://example.com" title="W3C Example"'
        attr1 = HTMLAttribute(
            raw='href="http://example.com"', ident='href',
            value='http://example.com')
        attr2 = HTMLAttribute(
            raw='title="W3C Example"', start=17,
            ident='title', value='W3C Example')
        attrs = HTMLAttributes(raw=attr_text, attributes=[attr1, attr2])
        self.assertEqual(attr_text, text_type(attrs))

    def test_as_dict_empty(self):
        attrs = HTMLAttributes(raw=' ')
        self.assertEqual(attrs.as_dict(), {})

    def test_as_dict_attrs(self):
        attr = HTMLAttribute(raw='foo=bar', ident='foo', value='bar')
        attrs = HTMLAttributes(raw='foo=bar', attributes=[attr])
        self.assertEqual(attrs.as_dict(), {'foo': 'bar'})


class TestHTMLOpenTag(TestCase):
    def test_str_with_attrs(self):
        raw = '<p class="headline">'
        attr = HTMLAttribute(
            raw='class="headline"', start=3, ident='class', value='headline')
        attrs = HTMLAttributes(
            raw='class="headline"', start=3, attributes=[attr])
        tag = HTMLOpenTag(
            raw='<a href="http://example.com">', tag='p', attributes=attrs)
        self.assertEqual(raw, text_type(tag))

    def test_str_without_attrs(self):
        raw = '<strong>'
        attrs = HTMLAttributes(start=3)
        tag = HTMLOpenTag(raw='<strong>', tag='strong', attributes=attrs)
        self.assertEqual(raw, text_type(tag))

    def assert_validate_attributes(
            self, attrs_dict, actions, expected_attrs_dict, issues=None):
        attrs = []
        start = 3
        for ident in sorted(attrs_dict):
            value = attrs_dict[ident]
            raw = '{}="{}"'.format(ident, value)
            attrs.append(
                HTMLAttribute(raw=raw, start=start, ident=ident, value=value))
            start += len(raw) + 1
        attrs_raw = ' '.join(attr.raw for attr in attrs)
        html_attrs = HTMLAttributes(raw=attrs_raw, start=3, attributes=attrs)
        if attrs_raw:
            tag_raw = '<a {}>'.format(attrs_raw)
        else:
            tag_raw = '<a>'
        tag = HTMLOpenTag(
            raw=tag_raw, tag='a', attributes=html_attrs,
            attribute_actions=actions)
        attributes = tag.attributes.as_dict()
        self.assertEqual(expected_attrs_dict, attributes)
        self.assertEqual(issues or [], tag.issues)

    def test_validate_default_keep(self):
        attr_dict = {'href': 'http://example.com'}
        actions = {None: 'keep'}
        self.assert_validate_attributes(attr_dict, actions, attr_dict)

    def test_validate_default_drop(self):
        attr_dict = {'href': 'http://example.com'}
        actions = {None: 'drop'}
        self.assert_validate_attributes(attr_dict, actions, {})

    def test_validate_default_ban(self):
        actions = {None: 'ban'}
        attr_dict = {'href': 'http://example.com'}
        issue = (
            'unexpected_attribute', 3, 28,
            {'node_type': 'a', 'ident': 'href', 'value': 'http://example.com',
             'expected': 'no attributes'})
        self.assert_validate_attributes(attr_dict, actions, {}, [issue])

    def test_validate_must_is_present(self):
        actions = {None: 'drop', 'href': 'must'}
        attr_dict = {'href': 'http://example.com'}
        self.assert_validate_attributes(attr_dict, actions, attr_dict)

    def test_validate_must_is_missing(self):
        actions = {None: 'drop', 'href': 'must'}
        issue = (
            'missing_attribute', 0, 3, {'node_type': 'a', 'ident': 'href'})
        self.assert_validate_attributes({}, actions, {}, [issue])

    def test_validate_missing_and_unexpected(self):
        actions = {None: 'drop', 'external': 'ban', 'href': 'must'}
        ban_issue = (
            'unexpected_attribute', 3, 15,
            {'node_type': 'a', 'ident': 'external', 'value': '1',
             'expected': 'the attribute href'})
        missing_issue = (
            'missing_attribute', 0, 16, {'node_type': 'a', 'ident': 'href'})
        self.assert_validate_attributes(
            {'external': '1'}, actions, {}, [ban_issue, missing_issue])

    def test_validate_unexpected_2_musts(self):
        actions = {
            None: 'drop', 'external': 'must', 'href': 'must', 'style': 'ban'}
        issue = (
            'unexpected_attribute', 42, 62,
            {'node_type': 'a', 'ident': 'style', 'value': 'display:none',
             'expected': 'the attributes external or href'})
        expected = {'href': 'http://example.com', 'external': '1'}
        passed = expected.copy()
        passed['style'] = 'display:none'
        self.assert_validate_attributes(passed, actions, expected, [issue])


class TestHTMLCloseTag(TestCase):
    def test_str(self):
        raw = '</p>'
        tag = HTMLCloseTag(raw=raw, tag='p')
        self.assertEqual(raw, text_type(tag))


class TestHTMLElement(TestCase):
    def test_str(self):
        raw = '<p class="first">A Text Element</p>'
        attr = HTMLAttribute(
            raw='class="first"', start=3, ident='class', value='first')
        attrs = HTMLAttributes(raw='class="first"', start=3, attributes=[attr])
        open_tag = HTMLOpenTag(
            raw='<p class="first">', tag='p', attributes=attrs)
        close_tag = HTMLCloseTag(raw='</p>', start=31, tag='p')
        children = [HTMLInterval(raw='A Text Element', start=17)]
        element = HTMLElement(
            raw=raw, open_tag=open_tag, close_tag=close_tag, children=children)
        self.assertEqual(raw, str(element))

    def test_to_text(self):
        raw = '<p>A <strong>Text</strong> Element</p>'
        strong_attrs = HTMLAttributes(raw='', attributes=[])
        strong_open_tag = HTMLOpenTag(
            raw='<strong>', tag='strong', attributes=strong_attrs)
        strong_close_tag = HTMLCloseTag(raw='</strong>', tag='strong')
        strong_text = HTMLText(raw='Text')
        strong_elem = HTMLElement(
            raw='<strong>Text</strong>', open_tag=strong_open_tag,
            close_tag=strong_close_tag, children=[strong_text])
        p_attrs = HTMLAttributes(raw='', attributes=[])
        p_open_tag = HTMLOpenTag(raw='<p>', tag='p', attributes=p_attrs)
        p_close_tag = HTMLCloseTag(raw='</p>', tag='p')
        text1 = HTMLText(raw='A ')
        text2 = HTMLText(raw=' Element')
        p_elem = HTMLElement(
            raw=raw, open_tag=p_open_tag, close_tag=p_close_tag,
            children=[text1, strong_elem, text2])
        self.assertEqual('A Text Element', p_elem.to_text())

    def test_br_to_html(self):
        raw = '<br>'
        attrs = HTMLAttributes()
        open_tag = HTMLOpenTag(raw=raw, tag='br', attributes=attrs)
        element = HTMLElement(raw=raw, open_tag=open_tag)
        self.assertEqual(raw, element.to_html())

    def test_br_to_html_drop_tag(self):
        raw = '<br>'
        attrs = HTMLAttributes()
        open_tag = HTMLOpenTag(raw=raw, tag='br', attributes=attrs)
        element = HTMLElement(raw=raw, open_tag=open_tag, drop_tag=True)
        self.assertEqual('', element.to_html())


class TestGrammar(TestCase):
    def test_simple_paragraph(self):
        text = '<p>This is a simple paragraph.</p>'
        parsed = html_grammar['html'].parse(text)
        assert parsed

    def test_simple_text(self):
        text = 'This is simple text'
        parsed = html_grammar['html'].parse(text)
        assert parsed

    def test_empty_tag(self):
        text = '<td></td>'
        parsed = html_grammar['html'].parse(text)
        assert parsed

    def test_double_quoted(self):
        text = '"text"'
        parsed = html_grammar['double_quoted_text'].parse(text)
        self.assertEqual('text', parsed.match.group('content'))

    def test_double_quoted_with_escape(self):
        text = '"\\"text\\""'
        parsed = html_grammar['double_quoted_text'].parse(text)
        self.assertEqual('\\"text\\"', parsed.match.group('content'))


class TestVisitor(TestCase):
    def setUp(self):
        self.visitor = HTMLVisitor()

    def assert_attrs(self, text, expected_attrs):
        parsed = html_grammar['attrs'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.as_dict(), expected_attrs)

    def test_attrs_empty(self):
        self.assert_attrs('', {})

    def test_attrs_mixed(self):
        text = 'foo="bar" key=\'value\' selected=1'
        expected = {'foo': 'bar', 'key': 'value', 'selected': 1}
        self.assert_attrs(text, expected)

    def test_option_selected(self):
        text = '<option value="value2" selected>Value 2</option>'
        parsed = html_grammar['option_element'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertIsInstance(out, HTMLElement)

    def test_open(self):
        text = '<a href="http://example.com">'
        parsed = html_grammar['a_open'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.start, 0)
        self.assertEqual(out.end, len(text))
        self.assertEqual(out.tag, 'a')
        self.assertEqual(
            out.attributes.as_dict(), {'href': 'http://example.com'})

    def test_br(self):
        text = '<br>'
        parsed = html_grammar['br_element'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.start, 0)
        self.assertEqual(out.end, len(text))
        self.assertEqual(out.tag, 'br')

    def test_element(self):
        text = '<p>This is a simple paragraph.</p>'
        parsed = html_grammar['p_element'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.start, 0)
        self.assertEqual(out.end, len(text))
        self.assertEqual(out.open_tag.tag, 'p')
        self.assertEqual(out.open_tag.start, 0)
        self.assertEqual(out.open_tag.end, text.index('>') + 1)
        self.assertEqual(out.close_tag.tag, 'p')
        self.assertEqual(out.close_tag.start, text.index('</p>'))
        self.assertEqual(out.close_tag.end, len(text))
        self.assertEqual(out.tag, 'p')
        self.assertEqual(len(out.children), 1)
        self.assertEqual(
            out.children[0].raw, 'This is a simple paragraph.')

    def test_text_block(self):
        text = 'This is a simple paragraph.'
        parsed = html_grammar['text_block'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].start, 0)
        self.assertEqual(out[0].end, len(text))
        self.assertEqual(out[0].raw, 'This is a simple paragraph.')

    def test_html_simple_element(self):
        text = '<p>Simple Paragraph</p>'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], HTMLElement)
        self.assertEqual(out[0].tag, 'p')

    def test_html_simple_text(self):
        text = 'Simple Text'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], HTMLInterval)
        self.assertEqual(out[0].raw, 'Simple Text')
        self.assertEqual(out[0].start, 0)

    def test_html_simple_text_with_offset(self):
        text = 'Simple Text'
        parsed = html_grammar['html'].parse(text)
        self.visitor.offset = 100
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].raw, 'Simple Text')
        self.assertEqual(out[0].start, 100)

    def test_html_complex(self):
        text = '''
<p>
    Paragraph 1
</p>
<p>
    Paragraph 2
</p>
'''
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 5)
        self.assertIsInstance(out[0], HTMLText)
        self.assertEqual(str(out[0]), '')
        self.assertIsInstance(out[1], HTMLElement)
        self.assertEqual(str(out[1]), '<p>Paragraph 1</p>')
        self.assertIsInstance(out[2], HTMLText)
        self.assertEqual(str(out[2]), '')
        self.assertIsInstance(out[3], HTMLElement)
        self.assertEqual(str(out[3]), '<p>Paragraph 2</p>')
        self.assertIsInstance(out[4], HTMLText)
        self.assertEqual(str(out[4]), '')

    def test_html_with_code(self):
        text = '<p>Here is <code>code</code>.</p>'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        p_elem = out[0]
        self.assertIsInstance(p_elem, HTMLElement)
        self.assertEqual('p', p_elem.tag)
        text1, code, text2 = p_elem.children
        self.assertEqual(text_type(text1), 'Here is')
        self.assertEqual(text_type(code), '<code>code</code>')
        self.assertEqual(text_type(text2), '.')

    def test_html_simple_table(self):
        text = '<table><tr><td>A very dumb table</td></tr></table>'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        table = out[0]
        self.assertEqual(table.tag, 'table')
        self.assertEqual(len(table.children), 1)
        tr = table.children[0]
        self.assertEqual(tr.tag, 'tr')
        self.assertEqual(len(tr.children), 1)
        td = tr.children[0]
        self.assertEqual(td.tag, 'td')
        self.assertEqual(len(td.children), 1)
        text = td.children[0]
        self.assertEqual(text_type(text), 'A very dumb table')

    def test_html_empty_tag(self):
        text = '<td></td>'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        td = out[0]
        self.assertEqual(td.tag, 'td')
        self.assertEqual(len(td.children), 1)
        text = td.children[0]
        self.assertEqual(text_type(text), '')

    def test_add_issue(self):
        text = '<p>A paragraph</p>'
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertFalse(self.visitor.issues)
        self.assertEqual(len(out), 1)
        p_elem = out[0]
        self.visitor.add_issue('halt_import', p_elem)
        self.assertEqual(self.visitor.issues, [('halt_import', 0, 18, {})])

    def test_html_headers(self):
        text = """\
<h1>An H1 Header</h1>
<p>This is in the h1 section</p>
"""
        parsed = html_grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertFalse(self.visitor.issues)
        h1_elem, text1, p_elem, text2 = out
        self.assertIsInstance(h1_elem, HnElement)
        self.assertEqual(text_type(h1_elem), '<h1>An H1 Header</h1>')
        self.assertIsInstance(text1, HTMLText)
        self.assertEqual(text_type(text1), '')
        self.assertIsInstance(p_elem, HTMLElement)
        self.assertEqual(text_type(p_elem), '<p>This is in the h1 section</p>')
        self.assertIsInstance(text2, HTMLText)
        self.assertEqual(text_type(text2), '')

    def test_double_quoted_text(self):
        text = '"text"'
        parsed = html_grammar['text'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(['text'], out)

    def test_double_quoted_escaped_text(self):
        text = '"the \\"text\\"."'
        parsed = html_grammar['text'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(['the "text".'], out)

    def test_single_quoted_escaped_text(self):
        text = "'I don\\'t like escaped text'"
        parsed = html_grammar['text'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(["I don't like escaped text"], out)
