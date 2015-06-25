# coding: utf-8
"""Test mdn.specifications"""
from __future__ import unicode_literals

from parsimonious.grammar import Grammar

from mdn.html import HTMLText
from mdn.kumascript import kumascript_grammar, SpecName
from mdn.specifications import Spec2Visitor, SpecDescVisitor, SpecNameVisitor
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
            'kumascript_wrong_args', 4, 15,
            {'name': 'Spec2', 'args': [], 'scope': 'specification maturity',
             'kumascript': '{{Spec2}}', 'min': 1, 'max': 1, 'count': 0,
             'arg_names': ['SpecKey'], 'arg_count': '0 arguments',
             'arg_spec': 'exactly 1 argument (SpecKey)'})]
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


class TestSpecDescVisitor(TestCase):
    def setUp(self):
        self.visitor = SpecDescVisitor()

    def assert_specdesc(self, html, items, issues):
        parsed = grammar.parse(html)
        self.visitor.visit(parsed)
        actual = [item.to_html() for item in self.visitor.desc_items]
        self.assertEqual(items, actual)
        self.assertEqual(self.visitor.issues, issues)

    def test_empty(self):
        self.assert_specdesc('<td></td>', [''], [])

    def test_plain_text(self):
        self.assert_specdesc('<td> Plain text </td>', ['Plain text'], [])

    def test_html(self):
        html = "<td>Defines <code>right</code> as animatable.</td>"
        expected = ["Defines", "<code>right</code>", "as animatable."]
        self.assert_specdesc(html, expected, [])

    def test_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        html = """<td style=\"vertical-align: top;\">
            Initial definition.
        </td>"""
        expected = ["Initial definition."]
        self.assert_specdesc(html, expected, [])

    def test_kumascript(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/vertical-align
        html = (
            '<td>Add the {{ xref_csslength() }} value and allows it to be'
            ' applied to element with a {{ cssxref("display") }} type of'
            ' <code>table-cell</code>.</td>')
        expected = [
            'Add the', '<code>&lt;length&gt;</code>',
            'value and allows it to be applied to element with a',
            '<code>display</code>', 'type of', '<code>table-cell</code>', '.']
        self.assert_specdesc(html, expected, [])

    def test_kumascript_spec2(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data
        html = "<td>No change from {{Spec2('HTML5 W3C')}}</td>"
        expected = ["No change from", "specification HTML5 W3C"]
        issues = [
            ('specdesc_spec2_invalid', 19, 41,
             {'name': 'Spec2', 'args': ['HTML5 W3C'],
              'scope': 'specification description',
              'kumascript': '{{Spec2("HTML5 W3C")}}'})]
        self.assert_specdesc(html, expected, issues)

    def test_kumascript_experimental_inline(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/position_value
        html = (
            '<td>Defines <code>&lt;position&gt;</code> explicitly and extends'
            ' it to support offsets from any edge. {{ experimental_inline() }}'
            '</td>')
        expected = [
            'Defines', '<code>&lt;position&gt;</code>',
            'explicitly and extends it to support offsets from any edge.', '']
        self.assert_specdesc(html, expected, [])
