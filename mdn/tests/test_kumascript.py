# coding: utf-8
"""Test mdn.kumascript."""
from __future__ import unicode_literals

from django.utils.six import text_type
from parsimonious.grammar import Grammar

from mdn.html import HTMLText
from mdn.kumascript import (
    kumascript_grammar, KumaScript, KnownKumaScript, KumaVisitor, SpecName,
    Spec2)
from webplatformcompat.models import Specification
from .base import TestCase
from .test_html import TestGrammar as TestHTMLGrammar
from .test_html import TestVisitor as TestHTMLVisitor

grammar = Grammar(kumascript_grammar)


class TestKumaScript(TestCase):
    def test_str_args(self):
        ks = KumaScript(
            '{{CompatGeckoDesktop("1.9")}}', 0, 'CompatGeckoDesktop', ["1.9"])
        self.assertEqual('{{CompatGeckoDesktop("1.9")}}', text_type(ks))

    def test_str_args_double_quote(self):
        self.get_instance(Specification, 'css3_display')
        ks = KumaScript(
            "{{SpecName('CSS3 Display', '#display', '\"display\"')}}", 0,
            "SpecName", ['CSS3 Display', '#display', '"display"'])
        self.assertEqual(
            '{{SpecName("CSS3 Display", "#display", \'"display"\')}}',
            text_type(ks))

    def test_str_no_args(self):
        ks = KumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertEqual('{{CompatNo}}', text_type(ks))

    def test_to_html(self):
        ks = KumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertEqual('', ks.to_html())

    def test_known(self):
        ks = KumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertFalse(ks.known)


class TestKnownKumaScript(TestCase):
    def test_known(self):
        ks = KnownKumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertTrue(ks.known)


class TestSpecName(TestCase):
    def test_3args(self):
        self.get_instance(Specification, 'css3_backgrounds')
        raw = ("{{SpecName('CSS3 Backgrounds', '#the-background-size',"
               "'background-size')}}")
        ks = SpecName(
            raw, 0, 'SpecName',
            ['CSS3 Backgrounds', '#the-background-size', 'background-size'])
        self.assertEqual(ks.mdn_key, 'CSS3 Backgrounds')
        self.assertEqual(ks.subpath, '#the-background-size')
        self.assertEqual(ks.section_name, 'background-size')
        self.assertFalse(ks.issues)

    def test_1arg(self):
        self.get_instance(Specification, 'css3_backgrounds')
        raw = "{{SpecName('CSS3 Backgrounds')}}"
        ks = SpecName(raw, 0, 'SpecName', ['CSS3 Backgrounds'], 'test')
        self.assertEqual(ks.mdn_key, 'CSS3 Backgrounds')
        self.assertEqual(ks.subpath, None)
        self.assertEqual(ks.section_name, None)
        self.assertFalse(ks.issues)

    def test_blank_mdn_key(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MIDIConnectionEvent
        raw = "{{SpecName('', '#midiconnection')}}"
        ks = SpecName(raw, 0, 'SpecName', ['', '#midiconnection'], 'test')
        self.assertEqual(ks.mdn_key, '')
        self.assertEqual(ks.subpath, '#midiconnection')
        self.assertIsNone(ks.section_name, None)
        issue = ks._make_issue('specname_blank_key')
        self.assertEqual(ks.issues, [issue])


class TestGrammar(TestHTMLGrammar):
    def test_no_arg_kumascript(self):
        text = '<p>{{CompatNo}}</p>'
        parsed = grammar['html'].parse(text)
        assert parsed


class TestVisitor(TestHTMLVisitor):
    def setUp(self):
        self.visitor = KumaVisitor()
        self.visitor.scope = 'test'

    def assert_kumascript(self, text, name, args, known=True, issues=None):
        parsed = grammar['kumascript'].parse(text)
        ks = self.visitor.visit(parsed)
        self.assertIsInstance(ks, KumaScript)
        self.assertEqual(ks.name, name)
        self.assertEqual(ks.args, args)
        self.assertEqual(ks.known, known)
        self.assertEqual(ks.issues, issues or [])

    def test_kumascript_no_args(self):
        self.assert_kumascript('{{CompatNo}}', 'CompatNo', [])

    def test_kumascript_no_parens_and_spaces(self):
        self.assert_kumascript('{{ CompatNo }}', 'CompatNo', [])

    def test_kumascript_empty_parens(self):
        self.assert_kumascript('{{CompatNo()}}', 'CompatNo', [])

    def test_kumascript_one_arg(self):
        self.assert_kumascript(
            '{{cssxref("-moz-border-image")}}', 'cssxref',
            ['-moz-border-image'])

    def test_kumascript_one_arg_no_quotes(self):
        self.assert_kumascript(
            '{{CompatGeckoDesktop(27)}}', 'CompatGeckoDesktop', ['27'])

    def test_kumascript_three_args(self):
        self.get_instance(Specification, 'css3_backgrounds')
        self.assert_kumascript(
            ("{{SpecName('CSS3 Backgrounds', '#the-background-size',"
             " 'background-size')}}"),
            "SpecName",
            ["CSS3 Backgrounds", "#the-background-size",
             "background-size"])

    def test_kumascript_empty_string(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MIDIConnectionEvent
        raw = "{{SpecName('', '#midiconnection')}}"
        name = "SpecName"
        args = ['', '#midiconnection']
        issue = (
            'specname_blank_key', 0, 35,
            {'name': name, 'args': args, 'scope': 'test',
             'kumascript': '{{SpecName("", "#midiconnection")}}'})
        self.assert_kumascript(raw, name, args, issues=[issue])

    def test_kumascript_unknown(self):
        issue = (
            'unknown_kumascript', 0, 10,
            {'name': 'CSSRef', 'args': [], 'scope': 'test',
             'kumascript': '{{CSSRef}}'})
        self.assert_kumascript("{{CSSRef}}", "CSSRef", [], False, [issue])

    def test_kumascript_in_html(self):
        html = """\
<tr>
   <td>{{SpecName('CSS3 Display', '#display', 'display')}}</td>
   <td>{{Spec2('CSS3 Display')}}</td>
   <td>Added the <code>run-in</code> and <code>contents</code> values.</td>
</tr>"""
        parsed = grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        tr = out[0]
        self.assertEqual(tr.tag, 'tr')
        texts = [None] * 4
        texts[0], td1, texts[1], td2, texts[2], td3, texts[3] = tr.children
        for text in texts:
            self.assertIsInstance(text, HTMLText)
            self.assertFalse(text.cleaned)
        self.assertEqual(td1.tag, 'td')
        self.assertEqual(len(td1.children), 1)
        self.assertIsInstance(td1.children[0], SpecName)
        self.assertEqual(td2.tag, 'td')
        self.assertEqual(len(td2.children), 1)
        self.assertIsInstance(td2.children[0], Spec2)
        self.assertEqual(td3.tag, 'td')
        text1, code1, text2, code2, text3 = td3.children
        self.assertEqual(str(text1), 'Added the')
        self.assertEqual(str(code1), '<code>run-in</code>')
        self.assertEqual(str(text2), 'and')
        self.assertEqual(str(code2), '<code>contents</code>')
        self.assertEqual(str(text3), 'values.')
