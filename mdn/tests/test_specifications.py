# coding: utf-8
"""Test mdn.specifications"""
from __future__ import unicode_literals

from parsimonious.grammar import Grammar

from mdn.html import HTMLText
from mdn.kumascript import kumascript_grammar, SpecName
from mdn.specifications import SpecNameVisitor, Spec2Visitor
from webplatformcompat.models import Specification
from .base import TestCase

grammar = Grammar(kumascript_grammar)


class TestSpecNameVisitor(TestCase):
    def setUp(self):
        self.visitor = SpecNameVisitor()

    def assert_specname(self, html, mdn_key, subpath, section_name, issues):
        parsed = grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        self.assertTrue(out)
        self.assertEqual(self.visitor.mdn_key, mdn_key)
        self.assertEqual(self.visitor.subpath, subpath)
        self.assertEqual(self.visitor.section_name, section_name)
        self.assertEqual(self.visitor.issues, issues)

    def test_no_specname(self):
        html = "<td>No spec</td>"
        expected_issue = (
            'specname_not_kumascript', 4, 11, {'original': u'No spec'})
        self.assert_specname(html, None, None, None, [expected_issue])
        self.assertIsNone(self.visitor.spec_item)

    def test_has_specname_kumascript(self):
        spec = self.get_instance(Specification, 'css3_ui')
        html = "<td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}</td>"
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [])
        self.assertIsInstance(self.visitor.spec_item, SpecName)
        self.assertEqual(self.visitor.spec_item.spec, spec)

    def test_has_specname_unknown_spec(self):
        html = "<td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}</td>"
        expected = ('unknown_spec', 4, 50, {'key': 'CSS3 UI'})
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [expected])
        self.assertIsInstance(self.visitor.spec_item, SpecName)
        self.assertIsNone(self.visitor.spec_item.spec)

    def test_has_specname_kumascript_whitespace(self):
        spec = self.get_instance(Specification, 'css3_ui')
        html = "<td>\n  {{ SpecName('CSS3 UI', '#cursor', 'cursor') }}\n</td>"
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [])
        self.assertIsInstance(self.visitor.spec_item, SpecName)
        self.assertEqual(self.visitor.spec_item.spec, spec)

    def test_commas(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
        spec = self.get_instance(Specification, 'html_whatwg')
        html = "<td>{{SpecName('HTML WHATWG',\
 'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements',\
 '&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;, and &lt;h6&gt;'\
 )}}</td>"
        self.assert_specname(
            html, 'HTML WHATWG',
            'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements',
            ('&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;,'
             ' and &lt;h6&gt;'), [])
        self.assertIsInstance(self.visitor.spec_item, SpecName)
        self.assertEqual(self.visitor.spec_item.spec, spec)

    def test_ES1_legacy(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/this
        self.get_instance(Specification, 'es1')
        html = "<td>ECMAScript 1st Edition.</td>"
        expected_issue = (
            'specname_converted', 4, 27,
            {'key': 'ES1', 'original': 'ECMAScript 1st Edition.'})
        self.assert_specname(html, 'ES1', None, None, [expected_issue])
        self.assertIsInstance(self.visitor.spec_item, HTMLText)

    def test_specname_td_ES3_legacy(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/function
        html = "<td> ECMAScript 3rd Edition. </td>"
        issue1 = (
            'specname_converted', 4, 29,
            {'original': 'ECMAScript 3rd Edition.', 'key': 'ES3'})
        issue2 = ('unknown_spec', 4, 29, {'key': 'ES3'})
        self.assert_specname(html, 'ES3', None, None, [issue1, issue2])
        self.assertIsInstance(self.visitor.spec_item, HTMLText)


class TestSpec2Visitor(TestCase):
    def setUp(self):
        self.visitor = Spec2Visitor()

    def assert_spec2(self, html, mdn_key, issues):
        parsed = grammar.parse(html)
        out = self.visitor.visit(parsed)
        self.assertTrue(out)
        self.assertEqual(self.visitor.mdn_key, mdn_key)
        self.assertEqual(self.visitor.issues, issues)

    def test_standard(self):
        spec = self.get_instance(Specification, 'css3_ui')
        html = '<td>{{Spec2("CSS3 UI")}}</td>'
        self.assert_spec2(html, 'CSS3 UI', [])
        self.assertEqual(self.visitor.spec, spec)
        self.assertEqual(self.visitor.maturity, spec.maturity)

    def test_empty(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MIDIInput
        html = '<td>{{Spec2()}}</td>'
        issues = [(
            'spec2_arg_count', 4, 15,
            {'name': 'Spec2', 'args': [], 'scope': 'specification maturity',
             'kumascript': '{{Spec2}}'})]
        self.assert_spec2(html, None, issues)

    def test_specname(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/tabIndex
        spec = self.get_instance(Specification, 'html_whatwg')
        html = "<td>{{SpecName('HTML WHATWG')}}</td>"
        issues = [(
            'spec2_wrong_kumascript', 4, 31,
            {'name': 'SpecName', 'args': ["HTML WHATWG"],
             'scope': 'specification maturity',
             'kumascript': '{{SpecName("HTML WHATWG")}}'})]
        self.assert_spec2(html, 'HTML WHATWG', issues)
        self.assertEqual(self.visitor.spec, spec)
        self.assertEqual(self.visitor.maturity, spec.maturity)

    def test_text_name(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/this
        html = "<td>Standard</td>"
        self.assert_spec2(html, None, [])
