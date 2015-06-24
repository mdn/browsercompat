# coding: utf-8
"""Test mdn.kumascript."""
from __future__ import unicode_literals

from django.utils.six import text_type
from parsimonious.grammar import Grammar

from mdn.html import HTMLText
from mdn.kumascript import (
    CSSBox, CSSxRef, CompatAndroid, CompatGeckoDesktop, CompatGeckoFxOS,
    CompatGeckoMobile, CompatNo, CompatUnknown, CompatVersionUnknown,
    CompatibilityTable, DOMxRef, DeprecatedInline, ExperimentalInline,
    HTMLElement, KnownKumaScript, KumaScript, KumaVisitor, NonStandardInline,
    NotStandardInline, PropertyPrefix, Spec2, SpecName, XrefCSSLength,
    kumascript_grammar)
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

    def test_known(self):
        ks = KumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertFalse(ks.known)


class TestKnownKumaScript(TestCase):
    def test_known(self):
        ks = KnownKumaScript('{{CompatNo}}', 0, 'CompatNo', [])
        self.assertTrue(ks.known)


class TestCompatAndroid(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatAndroid
    def test_standard(self):
        raw = "{{CompatAndroid(1.0)}}"
        ks = CompatAndroid(raw, 0, 'CompatAndroid', ['1.0'], 'test')
        self.assertEqual(ks.version, '1.0')
        self.assertEqual(ks.to_html(), '1.0')
        self.assertFalse(ks.issues)


class TestCompatGeckoDesktop(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoDesktop
    def assert_value(self, gecko_version, version, issues=[]):
        raw = '{{CompatGeckoDesktop("{}")}}'.format(gecko_version)
        ks = CompatGeckoDesktop(
            raw, 0, 'CompatGeckoDesktop', [gecko_version], 'test')
        self.assertEqual(ks.gecko_version, gecko_version)
        self.assertEqual(ks.version, version)
        self.assertEqual(ks.to_html(), version)
        self.assertEqual(ks.issues, issues or [])

    def test_v1(self):
        self.assert_value("1", "1.0")

    def test_v8(self):
        self.assert_value("8.0", "8.0")

    def test_bad_text(self):
        self.assert_value(
            "Yep", None,
            [('compatgeckodesktop_unknown', 0, 27, {'version': 'Yep'})])

    def test_bad_num(self):
        self.assert_value(
            "1.1", None,
            [('compatgeckodesktop_unknown', 0, 27, {'version': '1.1'})])


class TestCompatGeckoFxOS(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoFxOS
    def assert_value(self, gecko_version, version, issues=[]):
        raw = '{{CompatGeckoFxOS("{}")}}'.format(gecko_version)
        ks = CompatGeckoFxOS(
            raw, 0, 'CompatGeckoFxOS', [gecko_version], 'test')
        self.assertEqual(ks.gecko_version, gecko_version)
        self.assertEqual(ks.version, version)
        self.assertEqual(ks.to_html(), version)
        self.assertEqual(ks.issues, issues or [])

    def test_7(self):
        self.assert_value('7', '1.0')

    def test_range(self):
        versions = {'10': '1.0',
                    '24': '1.2',
                    '28': '1.3',
                    '29': '1.4',
                    '32': '2.0',
                    '34': '2.1',
                    '35': '2.2'
                    }
        for gversion, oversion in versions.items():
            self.assert_value(gversion, oversion)

    def test_bad_gecko(self):
        self.assert_value(
            "999999", None,
            issues=[('compatgeckofxos_unknown', 0, 27, {'version': '999999'})])

    def test_bad_text(self):
        self.assert_value(
            "Yep", None,
            issues=[('compatgeckofxos_unknown', 0, 24, {'version': 'Yep'})])

    def assert_value_with_override(
            self, gecko_version, override, version, issues=[]):
        raw = '{{CompatGeckoFxOS("{}", "{}")}}'.format(gecko_version, override)
        ks = CompatGeckoFxOS(
            raw, 0, 'CompatGeckoFxOS', [gecko_version, override], 'test')
        self.assertEqual(ks.gecko_version, gecko_version)
        self.assertEqual(ks.version, override)
        self.assertEqual(ks.to_html(), override)
        self.assertEqual(ks.issues, issues or [])

    def test_7_override_1_0_1(self):
        self.assert_value_with_override("7", "1.0.1", "1.0.1")

    def test_7_override_1_1(self):
        self.assert_value_with_override("7", "1.1", "1.1")

    def test_bad_override(self):
        self.assert_value_with_override(
            "18", "5.0", None,
            issues=[('compatgeckofxos_override', 0, 30,
                     {'override': '5.0', 'version': '18'})])


class TestCompatGeckoMobile(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoMobile
    def assert_value(self, gecko_version, version, issues=[]):
        raw = '{{CompatGeckoMobile("{}")}}'.format(gecko_version)
        ks = CompatGeckoMobile(
            raw, 0, 'CompatGeckoMobile', [gecko_version], 'test')
        self.assertEqual(ks.gecko_version, gecko_version)
        self.assertEqual(ks.version, version)
        self.assertEqual(ks.to_html(), version)
        self.assertEqual(ks.issues, issues or [])

    def test_v1(self):
        self.assert_value("1", "1.0")

    def test_v1_11(self):
        self.assert_value("1.11", "1.0")

    def test_v2(self):
        self.assert_value("2", "4.0")


class TestCompatNo(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatNo
    def test_standard(self):
        raw = '{{CompatNo}}'
        ks = CompatNo(raw, 0, 'CompatNo', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)

    def test_passing_args_fails(self):
        raw = '{{CompatNo("14.0")}}'
        ks = CompatNo(raw, 0, 'CompatNo', ['14.0'], 'test')
        issue = ks._make_issue(
            'kumascript_wrong_args',
            {'min': 0, 'max': 0, 'count': 1, 'arg_names': [],
             'arg_spec': 'no arguments', 'arg_count': '1 argument'})
        self.assertEqual(ks.issues, [issue])


class TestCompatUnknown(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatUnknown
    def test_standard(self):
        raw = '{{CompatUnknown}}'
        ks = CompatUnknown(raw, 0, 'CompatUnknown', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestCompatVersionUnknown(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatVersionUnknown
    def test_standard(self):
        raw = '{{CompatVersionUnknown}}'
        ks = CompatVersionUnknown(raw, 0, 'CompatVersionUnknown', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestCompatibilityTable(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:CompatibilityTable
    def test_standard(self):
        raw = '{{CompatibilityTable}}'
        ks = CompatibilityTable(raw, 0, 'CompatibilityTable', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestHTMLElement(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:HTMLElement
    def assert_value(self, name, html):
        raw = '{{HTMLElement("{}")}}'.format(name)
        ks = HTMLElement(raw, 0, 'HTMLElement', [name], 'test')
        self.assertEqual(ks.to_html(), html)
        self.assertFalse(ks.issues)

    def test_standard(self):
        self.assert_value('isindex', '<code>&lt;isindex&gt;</code>')

    def test_spaces(self):
        self.assert_value('is index', '<code>is index</code>')


class TestSpec2(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:Spec2
    def test_standard(self):
        spec = self.get_instance(Specification, 'css3_backgrounds')
        raw = "{{Spec2('CSS3 Backgrounds')}}"
        ks = Spec2(raw, 0, 'Spec2', ['CSS3 Backgrounds'], 'test')
        self.assertEqual(ks.mdn_key, 'CSS3 Backgrounds')
        self.assertEqual(ks.spec, spec)
        self.assertEqual(ks.maturity, spec.maturity)
        self.assertFalse(ks.issues)

    def test_unknown_mdn_key(self):
        raw = "{{Spec2('CSS3 Backgrounds')}}"
        ks = Spec2(raw, 0, 'Spec2', ['CSS3 Backgrounds'], 'test')
        self.assertEqual(ks.mdn_key, 'CSS3 Backgrounds')
        self.assertIsNone(ks.spec)
        self.assertIsNone(ks.maturity)
        issues = [('unknown_spec', 0, 29, {'key': ks.mdn_key})]
        self.assertEqual(ks.issues, issues)

    def test_empty_key(self):
        raw = "{{Spec2()}}"
        ks = Spec2(raw, 0, 'Spec2', [], 'test')
        self.assertIsNone(ks.mdn_key)
        self.assertIsNone(ks.spec)
        self.assertIsNone(ks.maturity)
        expected = ks._make_issue(
            'kumascript_wrong_args',
            {'min': 1, 'max': 1, 'arg_names': ['SpecKey'], 'count': 0,
             'arg_count': '0 arguments',
             'arg_spec': 'exactly 1 argument (SpecKey)'})
        self.assertEqual(ks.issues, [expected])


class TestSpecName(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:SpecName
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

    def test_unknown_spec(self):
        raw = "{{SpecName('CSS3 Backgrounds')}}"
        ks = SpecName(raw, 0, 'SpecName', ['CSS3 Backgrounds'], 'test')
        self.assertEqual(ks.mdn_key, 'CSS3 Backgrounds')
        self.assertEqual(ks.subpath, None)
        self.assertEqual(ks.section_name, None)
        expected = [('unknown_spec', 0, 32, {'key': u'CSS3 Backgrounds'})]
        self.assertEqual(ks.issues, expected)

    def test_blank_mdn_key(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MIDIConnectionEvent
        raw = "{{SpecName('', '#midiconnection')}}"
        ks = SpecName(raw, 0, 'SpecName', ['', '#midiconnection'], 'test')
        self.assertEqual(ks.mdn_key, '')
        self.assertEqual(ks.subpath, '#midiconnection')
        self.assertIsNone(ks.section_name, None)
        issue = ks._make_issue('specname_blank_key')
        self.assertEqual(ks.issues, [issue])

    def test_no_args(self):
        raw = "{{SpecName}}"
        ks = SpecName(raw, 0, 'SpecName', [], 'test')
        issue = ks._make_issue(
            'kumascript_wrong_args',
            {'min': 1, 'max': 3, 'count': 0,
             'arg_names': ['SpecKey', 'Anchor', 'AnchorName'],
             'arg_count': '0 arguments',
             'arg_spec': (
                 'between 1 and 3 arguments (SpecKey, Anchor, [AnchorName])')
             })
        self.assertEqual(ks.issues, [issue])


class TestCSSBox(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:cssbox
    def test_standard(self):
        raw = '{{cssbox("background-clip")}}'
        ks = CSSBox(raw, 0, 'CSSBox', ['background-clip'], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertEqual(ks.issues, [])


class TestCSSxRef(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:cssxref
    def test_standard(self):
        raw = '{{cssxref("z-index")}}'
        ks = CSSxRef(raw, 0, 'cssxref', ['z-index'], 'test')
        self.assertEqual(ks.api_name, 'z-index')
        self.assertIsNone(ks.display_name)
        self.assertEqual(ks.to_html(), '<code>z-index</code>')
        self.assertEqual(ks.issues, [])

    def test_display_override(self):
        raw = '{{cssxref("the-foo", "foo")}}'
        ks = CSSxRef(raw, 0, 'cssxref', ['the-foo', 'foo'], 'test')
        self.assertEqual(ks.api_name, 'the-foo')
        self.assertEqual(ks.display_name, 'foo')
        self.assertEqual(ks.to_html(), '<code>foo</code>')
        self.assertEqual(ks.issues, [])


class TestDeprecatedInline(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:deprecated_inline
    def test_standard(self):
        raw = '{{deprecated_inline}}'
        ks = DeprecatedInline(raw, 0, 'DeprecatedInline', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestDOMxRef(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:domxref
    def test_standard(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/CharacterData
        raw = '{{domxref("ChildNode")}}'
        ks = DOMxRef(raw, 0, 'DOMxRef', ['ChildNode'], 'test')
        self.assertEqual(ks.to_html(), '<code>ChildNode</code>')
        self.assertFalse(ks.issues)

    def test_with_override(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent/initCustomEvent
        raw = '{{domxref("CustomEvent.CustomEvent", "CustomEvent()")}}'
        ks = DOMxRef(
            raw, 0, 'DOMxRef', ['CustomEvent.CustomEvent', 'CustomEvent()'],
            'test')
        self.assertEqual(ks.to_html(), '<code>CustomEvent()</code>')


class TestExperimentalInline(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:experimental_inline
    def test_standard(self):
        raw = '{{experimental_inline}}'
        ks = ExperimentalInline(raw, 0, 'experimental_inline', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestNonStandardInline(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:non-standard_inline
    def test_standard(self):
        raw = '{{non-standard_inline}}'
        ks = NonStandardInline(raw, 0, 'non-standard_inline', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestNotStandardInline(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:not_standard_inline
    def test_standard(self):
        raw = '{{not_standard_inline}}'
        ks = NotStandardInline(raw, 0, 'not_standard_inline', [], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestPropertyPrefix(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:property_prefix
    def test_standard(self):
        raw = '{{property_prefix("-webkit")}}'
        ks = PropertyPrefix(raw, 0, 'property_prefix', ['-webkit'], 'test')
        self.assertEqual(ks.to_html(), '')
        self.assertFalse(ks.issues)


class TestXrefCSSLength(TestCase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csslength
    def test_standard(self):
        raw = '{{xref_csslength()}}'
        ks = XrefCSSLength(raw, 0, 'xref_csslength', [], 'test')
        self.assertEqual('<code>&lt;length&gt;</code>', ks.to_html())
        self.assertEqual([], ks.issues)


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

    def test_kumascript_and_text_and_HTML(self):
        html = """\
<td>
  Add the {{ xref_csslength() }} value and allows it to be applied to
  element with a {{ cssxref("display") }} type of <code>table-cell</code>.
</td>"""
        parsed = grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        self.assertEqual(len(out), 1)
        tr = out[0]
        self.assertEqual(tr.tag, 'td')
        txts = [None] * 4
        ks = [None] * 2
        txts[0], ks[0], txts[1], ks[1], txts[2], code, txts[3] = tr.children
        for text in txts:
            self.assertIsInstance(text, HTMLText)
            self.assertTrue(text.cleaned)
        self.assertEqual('Add the', str(txts[0]))
        self.assertEqual(
            'value and allows it to be applied to element with a',
            str(txts[1]))
        self.assertEqual('type of', str(txts[2]))
        self.assertEqual('.', str(txts[3]))
        self.assertEqual('{{xref_csslength}}', str(ks[0]))
        self.assertEqual('{{cssxref("display")}}', str(ks[1]))
        self.assertEqual('<code>table-cell</code>', str(code))
