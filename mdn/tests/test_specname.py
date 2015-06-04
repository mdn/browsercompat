# coding: utf-8
"""Test mdn.specname."""
from __future__ import unicode_literals

from parsimonious.grammar import Grammar

from mdn.kumascript import kumascript_grammar
from mdn.specname import SpecNameVisitor
from webplatformcompat.tests.base import TestCase

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

    def test_has_specname_kumascript(self):
        html = "<td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}</td>"
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [])

    def test_has_specname_kumascript_whitespace(self):
        html = "<td>\n  {{ SpecName('CSS3 UI', '#cursor', 'cursor') }}\n</td>"
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [])

    def test_commas(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
        html = "<td>{{SpecName('HTML WHATWG',\
 'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements',\
 '&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;, and &lt;h6&gt;'\
 )}}</td>"
        self.assert_specname(
            html, 'HTML WHATWG',
            'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements',
            ('&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;,'
             ' and &lt;h6&gt;'), [])

    def test_ES1_legacy(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/this
        html = "<td>ECMAScript 1st Edition.</td>"
        expected_issue = (
            'specname_converted', 4, 27,
            {'key': 'ES1', 'original': 'ECMAScript 1st Edition.'})
        self.assert_specname(html, 'ES1', None, None, [expected_issue])

    def test_specname_td_ES3_legacy(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/function
        html = "<td> ECMAScript 3rd Edition. </td>"
        expected_issue = (
            'specname_converted', 4, 29,
            {'original': 'ECMAScript 3rd Edition.', 'key': 'ES3'})
        self.assert_specname(html, 'ES3', None, None, [expected_issue])
