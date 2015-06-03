# coding: utf-8
"""Test mdn.html."""
from __future__ import unicode_literals

from django.utils.six import text_type
from parsimonious.grammar import Grammar

from mdn.html import (
    html_grammar, HTMLAttribute, HTMLAttributes, HTMLCloseTag, HTMLInterval,
    HTMLOpenTag, HTMLSimpleTag, HTMLStructure, HTMLText, HTMLVisitor)
from webplatformcompat.tests.base import TestCase

grammar = Grammar(html_grammar)


class TestHTMLInterval(TestCase):
    def test_str(self):
        interval = HTMLInterval('Interval', 0)
        self.assertEqual('Interval', text_type(interval))

    def test_to_html(self):
        interval = HTMLInterval('Interval', 0)
        self.assertEqual('Interval', interval.to_html())


class TestHTMLText(TestCase):
    def test_str(self):
        text = HTMLText('\nSome Text\n', 0)
        self.assertEqual('Some Text', text_type(text))


class TestHTMLSimpleTag(TestCase):
    def test_str(self):
        tag = HTMLSimpleTag('<br/>', 10, 'br')
        self.assertEqual('<br>', text_type(tag))


class TestHTMLAttribute(TestCase):
    def test_str_string_value(self):
        attr = HTMLAttribute('foo="bar"', 0, 'foo', 'bar')
        self.assertEqual('foo="bar"', text_type(attr))

    def test_str_int_value(self):
        attr = HTMLAttribute('selected=1', 0, 'selected', 1)
        self.assertEqual('selected=1', text_type(attr))


class TestHTMLAttributes(TestCase):
    def test_str_empty(self):
        attrs = HTMLAttributes(' ', 0)
        self.assertEqual('', text_type(attrs))

    def test_str_attrs(self):
        attr_text = 'href="http://example.com" title="W3C Example"'
        attr1 = HTMLAttribute(
            'href="http://example.com"', 0, 'href', 'http://example.com')
        attr2 = HTMLAttribute(
            'title="W3C Example"', 17, 'title', 'W3C Example')
        attrs = HTMLAttributes(attr_text, 0, [attr1, attr2])
        self.assertEqual(attr_text, text_type(attrs))

    def test_as_dict_empty(self):
        attrs = HTMLAttributes(' ', 0)
        self.assertEqual(attrs.as_dict(), {})

    def test_as_dict_attrs(self):
        attr = HTMLAttribute('foo=bar', 0, 'foo', 'bar')
        attrs = HTMLAttributes('foo=bar', 0, [attr])
        self.assertEqual(attrs.as_dict(), {'foo': 'bar'})


class TestHTMLOpenTag(TestCase):
    def test_str_with_attrs(self):
        raw = '<p class="headline">'
        attr = HTMLAttribute('class="headline"', 3, 'class', 'headline')
        attrs = HTMLAttributes('class="headline"', 3, [attr])
        tag = HTMLOpenTag('<a href="http://example.com">', 0, 'p', attrs)
        self.assertEqual(raw, text_type(tag))

    def test_str_without_attrs(self):
        raw = '<strong>'
        attrs = HTMLAttributes('', 3, [])
        tag = HTMLOpenTag('<strong>', 0, 'strong', attrs)
        self.assertEqual(raw, text_type(tag))


class TestHTMLCloseTag(TestCase):
    def test_str(self):
        raw = "</p>"
        tag = HTMLCloseTag(raw, 0, 'p')
        self.assertEqual(raw, text_type(tag))


class TestHTMLStructure(TestCase):
    def test_str(self):
        raw = '<p class="first">A Text Element</p>'
        attr = HTMLAttribute('class="first"', 3, 'class', 'first')
        attrs = HTMLAttributes('class="first"', 3, [attr])
        open_tag = HTMLOpenTag('<p class="first">', 0, 'p', attrs)
        close_tag = HTMLCloseTag('</p>', 31, 'p')
        content = [HTMLInterval('A Text Element', 17)]
        structure = HTMLStructure(raw, 0, open_tag, close_tag, content)
        self.assertEqual(raw, str(structure))


class TestGrammar(TestCase):
    def test_simple_paragraph(self):
        text = '<p>This is a simple paragraph.</p>'
        parsed = grammar['html'].parse(text)
        assert parsed

    def test_simple_text(self):
        text = 'This is simple text'
        parsed = grammar['html'].parse(text)
        assert parsed


class TestVisitor(TestCase):
    def setUp(self):
        self.visitor = HTMLVisitor()

    def assert_attrs(self, text, expected_attrs):
        parsed = grammar['attrs'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.as_dict(), expected_attrs)

    def test_attrs_empty(self):
        self.assert_attrs('', {})

    def test_attrs_mixed(self):
        text = 'foo="bar" key=\'value\' selected=1'
        expected = {'foo': 'bar', 'key': 'value', 'selected': 1}
        self.assert_attrs(text, expected)

    def test_open(self):
        text = '<a href="http://example.com">'
        parsed = grammar['a_open'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.start, 0)
        self.assertEqual(out.end, len(text))
        self.assertEqual(out.tag, 'a')
        self.assertEqual(out.attrs.as_dict(), {'href': 'http://example.com'})

    def test_br(self):
        text = '<br>'
        parsed = grammar['br'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(out.start, 0)
        self.assertEqual(out.end, len(text))
        self.assertEqual(out.tag, 'br')

    def test_tag(self):
        text = '<p>This is a simple paragraph.</p>'
        parsed = grammar['p_tag'].parse(text)
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
            out.children[0].raw_content, 'This is a simple paragraph.')

    def test_text_block(self):
        text = 'This is a simple paragraph.'
        parsed = grammar['text_block'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].start, 0)
        self.assertEqual(out[0].end, len(text))
        self.assertEqual(out[0].raw_content, 'This is a simple paragraph.')

    def test_html_simple_tag(self):
        text = '<p>Simple Paragraph</p>'
        parsed = grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], HTMLStructure)
        self.assertEqual(out[0].tag, 'p')

    def test_html_simple_text(self):
        text = 'Simple Text'
        parsed = grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], HTMLInterval)
        self.assertEqual(out[0].raw_content, 'Simple Text')
        self.assertEqual(out[0].start, 0)

    def test_html_simple_text_with_offset(self):
        text = 'Simple Text'
        parsed = grammar['html'].parse(text)
        self.visitor.offset = 100
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].raw_content, 'Simple Text')
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
        parsed = grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 5)
        self.assertIsInstance(out[0], HTMLText)
        self.assertEqual(str(out[0]), '')
        self.assertIsInstance(out[1], HTMLStructure)
        self.assertEqual(str(out[1]), '<p>Paragraph 1</p>')
        self.assertIsInstance(out[2], HTMLText)
        self.assertEqual(str(out[2]), '')
        self.assertIsInstance(out[3], HTMLStructure)
        self.assertEqual(str(out[3]), '<p>Paragraph 2</p>')
        self.assertIsInstance(out[4], HTMLText)
        self.assertEqual(str(out[4]), '')

    def test_html_with_code(self):
        text = "<p>Here is <code>code</code>.</p>"
        parsed = grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        p_elem = out[0]
        self.assertIsInstance(p_elem, HTMLStructure)
        self.assertEqual('p', p_elem.tag)
        text1, code, text2 = p_elem.children
        self.assertEqual(text_type(text1), 'Here is')
        self.assertEqual(text_type(code), '<code>code</code>')
        self.assertEqual(text_type(text2), '.')

    def test_html_simple_table(self):
        text = "<table><tr><td>A very dumb table</td></tr></table>"
        parsed = grammar['html'].parse(text)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        table = out[0]
        self.assertEqual(table.tag, "table")
        self.assertEqual(len(table.children), 1)
        tr = table.children[0]
        self.assertEqual(tr.tag, "tr")
        self.assertEqual(len(tr.children), 1)
        td = tr.children[0]
        self.assertEqual(td.tag, "td")
        self.assertEqual(len(td.children), 1)
        text = td.children[0]
        self.assertEqual(text_type(text), "A very dumb table")
