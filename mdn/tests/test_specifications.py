# coding: utf-8
"""Test mdn.specifications."""
from __future__ import unicode_literals

from webplatformcompat.models import Section

from mdn.html import HTMLText
from mdn.kumascript import KumaVisitor, SpecName, kumascript_grammar
from mdn.specifications import (
    SpecSectionExtractor, Spec2Visitor, SpecDescVisitor, SpecNameVisitor)
from .base import TestCase


class TestSpecSectionExtractor(TestCase):
    def setUp(self):
        self.visitor = KumaVisitor()
        self.spec = self.get_instance('Specification', 'css3_backgrounds')

    def construct_html(
            self, header=None, pre_table='', row=None, post_table=''):
        """Create a specification section with overrides."""
        header = header or """\
<h2 id="Specifications" name="Specifications">Specifications</h2>"""
        row = row or """\
<tr>
   <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',\
 'background-size')}}</td>
   <td>{{Spec2('CSS3 Backgrounds')}}</td>
   <td></td>
</tr>"""

        html = header + pre_table + """\
<table class="standard-table">
 <thead>
  <tr>
   <th scope="col">Specification</th>
   <th scope="col">Status</th>
   <th scope="col">Comment</th>
  </tr>
 </thead>
 <tbody>
""" + row + """
 </tbody>
</table>
""" + post_table
        return html

    def get_default_spec(self):
        return {
            'section.note': '',
            'section.subpath': '#the-background-size',
            'section.name': 'background-size',
            'specification.mdn_key': 'CSS3 Backgrounds',
            'section.id': None,
            'specification.id': self.spec.id,
        }

    def assert_extract(self, html, specs=None, issues=None):
        parsed = kumascript_grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        extractor = SpecSectionExtractor(elements=out)
        extracted = extractor.extract()
        self.assertEqual(extracted['specs'], specs or [])
        self.assertEqual(extracted['issues'], issues or [])

    def test_standard(self):
        html = self.construct_html()
        expected_spec = self.get_default_spec()
        self.assert_extract(html, [expected_spec])

    def test_key_mismatch(self):
        spec = self.get_instance('Specification', 'css3_ui')
        spec_row = '''\
<tr>
  <td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}</td>
  <td>{{ Spec2('CSS3 Basic UI') }}</td>
  <td>Addition of several keywords and the positioning syntax for\
 <code>url()</code>.</td>
</tr>'''
        html = self.construct_html(row=spec_row)
        expected_specs = [{
            'section.note': (
                'Addition of several keywords and the positioning syntax for'
                ' <code>url()</code>.'),
            'section.subpath': '#cursor',
            'section.name': 'cursor',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': spec.id}]
        issues = [
            ('unknown_spec', 309, 337, {'key': u'CSS3 Basic UI'}),
            ('spec_mismatch', 305, 342,
             {'spec2_key': 'CSS3 Basic UI', 'specname_key': 'CSS3 UI'})]
        self.assert_extract(html, expected_specs, issues)

    def test_known_spec(self):
        spec = self.get_instance('Specification', 'css3_backgrounds')
        self.create(Section, specification=spec)
        expected_spec = self.get_default_spec()
        expected_spec['specification.id'] = spec.id
        self.assert_extract(self.construct_html(), [expected_spec])

    def test_known_spec_and_section(self):
        section = self.get_instance('Section', 'background-size')
        spec = section.specification
        expected_spec = self.get_default_spec()
        expected_spec['specification.id'] = spec.id
        expected_spec['section.id'] = section.id
        self.assert_extract(self.construct_html(), [expected_spec], [])

    def test_es1(self):
        # en-US/docs/Web/JavaScript/Reference/Operators/this
        es1 = self.get_instance('Specification', 'es1')
        spec_row = """\
<tr>
  <td>ECMAScript 1st Edition.</td>
  <td>Standard</td>
  <td>Initial definition.</td>
</tr>"""
        html = self.construct_html(row=spec_row)
        expected_specs = [{
            'section.note': 'Initial definition.',
            'section.subpath': '',
            'section.name': '',
            'specification.mdn_key': 'ES1',
            'section.id': None,
            'specification.id': es1.id}]
        issues = [
            ('specname_converted', 251, 274,
             {'key': 'ES1', 'original': 'ECMAScript 1st Edition.'}),
            ('spec2_converted', 286, 294,
             {'key': 'ES1', 'original': 'Standard'})]
        self.assert_extract(html, expected_specs, issues)

    def test_nonstandard(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Promise (fixed)
        spec_row = """\
<tr>
   <td><a href="https://github.com/domenic/promises-unwrapping">\
domenic/promises-unwrapping</a></td>
   <td>Draft</td>
   <td>Standardization work is taking place here.</td>
</tr>"""
        html = self.construct_html(row=spec_row)
        expected_specs = [{
            'section.note': 'Standardization work is taking place here.',
            'section.subpath': '',
            'section.name': '',
            'specification.mdn_key': '',
            'section.id': None,
            'specification.id': None}]
        issues = [
            ('tag_dropped', 252, 309,
             {'tag': 'a', 'scope': 'specification name'}),
            ('specname_not_kumascript', 309, 336,
             {'original': 'domenic/promises-unwrapping'}),
            ('spec2_converted', 353, 358,
             {'key': '', 'original': 'Draft'})]
        self.assert_extract(html, expected_specs, issues)

    def test_spec2_td_no_spec(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MIDIInput
        spec = self.get_instance('Specification', 'css3_backgrounds')
        spec_row = """\
<tr>
   <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',\
 'background-size')}}</td>
   <td>{{Spec2()}}</td>
   <td></td>
</tr>"""
        html = self.construct_html(row=spec_row)
        expected_specs = [{
            'section.note': '',
            'section.subpath': '#the-background-size',
            'section.name': 'background-size',
            'specification.mdn_key': 'CSS3 Backgrounds',
            'section.id': None,
            'specification.id': spec.id}]
        issues = [(
            'kumascript_wrong_args', 340, 351,
            {'name': 'Spec2', 'args': [], 'scope': 'specification maturity',
             'kumascript': '{{Spec2}}', 'min': 1, 'max': 1, 'count': 0,
             'arg_names': ['SpecKey'], 'arg_count': '0 arguments',
             'arg_spec': 'exactly 1 argument (SpecKey)'})]
        self.assert_extract(html, expected_specs, issues)

    def test_specrow_empty(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/BluetoothGattService
        spec_row = """\
<tr>
   <td> </td>
   <td> </td>
   <td> </td>
</tr>"""
        html = self.construct_html(row=spec_row)
        expected_spec = {
            'section.note': '',
            'section.subpath': '',
            'section.name': '',
            'specification.mdn_key': '',
            'section.id': None,
            'specification.id': None}
        issues = [
            ('specname_omitted', 248, 258, {}),
            ('spec2_omitted', 262, 272, {})]
        self.assert_extract(html, [expected_spec], issues)

    def test_whynospec(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AnimationEvent/initAnimationEvent
        pre_table = """
<p>
{{WhyNoSpecStart}}
This method is non-standard and not part of any specification, though it was
present in early drafts of {{SpecName("CSS3 Animations")}}.
{{WhyNoSpecEnd}}
</p>"""
        html = self.construct_html(pre_table=pre_table)
        self.assert_extract(html, [self.get_default_spec()])

    def test_pre_table_content(self):
        pre_table = """
<p>
This method is non-standard and not part of any specification, though it was
present in early drafts of {{SpecName("CSS3 Animations")}}.
</p>"""
        html = self.construct_html(pre_table=pre_table)
        issues = [('skipped_content', 66, 211, {})]
        self.assert_extract(html, [self.get_default_spec()], issues)

    def test_post_table_content(self):
        post_table = (
            '<p>You may also be interested in the user group posts.</p>')
        html = self.construct_html(post_table=post_table)
        issues = [('skipped_content', 413, 471, {})]
        self.assert_extract(html, [self.get_default_spec()], issues)

    def test_h2_discards_extra(self):
        h2_extra = (
            '<h2 id="Specifications" name="Specifications" extra="crazy">'
            'Specifications</h2>')
        html = self.construct_html(header=h2_extra)
        self.assert_extract(html, [self.get_default_spec()])

    def test_h2_browser_compat(self):
        # Common bug from copying from Browser Compatibility section
        h2_browser_compat = (
            '<h2 id="Browser_compatibility" name="Browser_compatibility">'
            'Specifications</h2>')
        html = self.construct_html(header=h2_browser_compat)
        issues = [
            ('spec_h2_id', 4, 30, {'h2_id': 'Browser_compatibility'}),
            ('spec_h2_name', 31, 59, {'h2_name': 'Browser_compatibility'})]
        self.assert_extract(html, [self.get_default_spec()], issues)


class TestSpecNameVisitor(TestCase):
    def setUp(self):
        self.visitor = SpecNameVisitor()

    def assert_specname(self, html, mdn_key, subpath, section_name, issues):
        parsed = kumascript_grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        self.assertTrue(out)
        self.assertEqual(self.visitor.mdn_key, mdn_key)
        self.assertEqual(self.visitor.subpath, subpath)
        self.assertEqual(self.visitor.section_name, section_name)
        self.assertEqual(self.visitor.issues, issues)

    def test_no_specname(self):
        html = '<td>No spec</td>'
        expected_issue = (
            'specname_not_kumascript', 4, 11, {'original': u'No spec'})
        self.assert_specname(html, None, None, None, [expected_issue])
        self.assertIsNone(self.visitor.spec_item)

    def test_has_specname_kumascript(self):
        spec = self.get_instance('Specification', 'css3_ui')
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
        spec = self.get_instance('Specification', 'css3_ui')
        html = "<td>\n  {{ SpecName('CSS3 UI', '#cursor', 'cursor') }}\n</td>"
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [])
        self.assertIsInstance(self.visitor.spec_item, SpecName)
        self.assertEqual(self.visitor.spec_item.spec, spec)

    def test_commas(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
        spec = self.get_instance('Specification', 'html_whatwg')
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
        self.get_instance('Specification', 'es1')
        html = '<td>ECMAScript 1st Edition.</td>'
        expected_issue = (
            'specname_converted', 4, 27,
            {'key': 'ES1', 'original': 'ECMAScript 1st Edition.'})
        self.assert_specname(html, 'ES1', None, None, [expected_issue])
        self.assertIsInstance(self.visitor.spec_item, HTMLText)

    def test_specname_td_ES3_legacy(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/function
        html = '<td> ECMAScript 3rd Edition. </td>'
        issue1 = (
            'specname_converted', 4, 29,
            {'original': 'ECMAScript 3rd Edition.', 'key': 'ES3'})
        issue2 = ('unknown_spec', 4, 29, {'key': 'ES3'})
        self.assert_specname(html, 'ES3', None, None, [issue1, issue2])
        self.assertIsInstance(self.visitor.spec_item, HTMLText)

    def test_other_kumascript(self):
        self.get_instance('Specification', 'css3_ui')
        html = ("<td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}"
                '{{not_standard_inline}}</td>')
        kname = 'not_standard_inline'
        issue = (
            'unexpected_kumascript', 50, 73,
            {'args': [], 'kumascript': '{{%s}}' % kname,
             'name': kname, 'scope': 'specification name',
             'expected_scopes': 'compatibility feature'})
        self.assert_specname(html, 'CSS3 UI', '#cursor', 'cursor', [issue])


class TestSpec2Visitor(TestCase):
    def setUp(self):
        self.visitor = Spec2Visitor()

    def assert_spec2(self, html, mdn_key, issues):
        parsed = kumascript_grammar.parse(html)
        out = self.visitor.visit(parsed)
        self.assertTrue(out)
        self.assertEqual(self.visitor.mdn_key, mdn_key)
        self.assertEqual(self.visitor.issues, issues)

    def test_standard(self):
        spec = self.get_instance('Specification', 'css3_ui')
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
        self.get_instance('Specification', 'html_whatwg')
        html = "<td>{{SpecName('HTML WHATWG')}}</td>"
        issues = [(
            'unexpected_kumascript', 4, 31,
            {'name': 'SpecName', 'args': ['HTML WHATWG'],
             'scope': 'specification maturity',
             'kumascript': '{{SpecName("HTML WHATWG")}}',
             'expected_scopes': (
                'specification description or specification name')})]
        self.assert_spec2(html, None, issues)
        self.assertEqual(self.visitor.spec, None)

    def test_text_name(self):
        # /en-US/docs/Web/JavaScript/Reference/Operators/this
        html = '<td>Standard</td>'
        self.assert_spec2(html, None, [])

    def test_other_kumascript(self):
        self.get_instance('Specification', 'css3_ui')
        html = '<td>{{Spec2("CSS3 UI")}}{{deprecated_inline}}</td>'
        kname = 'deprecated_inline'
        issue = (
            'unexpected_kumascript', 24, 45,
            {'args': [], 'kumascript': '{{%s}}' % kname,
             'name': kname, 'scope': 'specification maturity',
             'expected_scopes': 'compatibility feature'})
        self.assert_spec2(html, 'CSS3 UI', [issue])


class TestSpecDescVisitor(TestCase):
    def setUp(self):
        self.visitor = SpecDescVisitor()

    def assert_specdesc(self, html, items, issues):
        parsed = kumascript_grammar.parse(html)
        self.visitor.visit(parsed)
        actual = [item.to_html() for item in self.visitor.desc_items]
        self.assertEqual(items, actual)
        self.assertEqual(self.visitor.issues, issues)

    def test_empty(self):
        self.assert_specdesc('<td></td>', [''], [])

    def test_plain_text(self):
        self.assert_specdesc('<td> Plain text </td>', ['Plain text'], [])

    def test_html(self):
        html = '<td>Defines <code>right</code> as animatable.</td>'
        expected = ['Defines', '<code>right</code>', 'as animatable.']
        self.assert_specdesc(html, expected, [])

    def test_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        html = """<td style=\"vertical-align: top;\">
            Initial definition.
        </td>"""
        expected = ['Initial definition.']
        issue = (
            'unexpected_attribute', 4, 32,
            {'expected': 'no attributes', 'node_type': 'td', 'ident': 'style',
             'value': 'vertical-align: top;'})
        self.assert_specdesc(html, expected, [issue])

    def test_kumascript(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/vertical-align
        html = (
            '<td>Add the {{ xref_csslength() }} value and allows it to be'
            ' applied to element with a {{ cssxref("display") }} type of'
            ' <code>table-cell</code>.</td>')
        expected = [
            'Add the',
            ('<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/'
             'length"><code>&lt;length&gt;</code></a>'),
            'value and allows it to be applied to element with a',
            ('<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/'
             'display"><code>display</code></a>'),
            'type of', '<code>table-cell</code>', '.']
        self.assert_specdesc(html, expected, [])

    def test_kumascript_spec2(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data
        html = "<td>No change from {{Spec2('HTML5 W3C')}}</td>"
        expected = ['No change from', 'specification HTML5 W3C']
        issues = [
            ('unexpected_kumascript', 19, 41,
             {'name': 'Spec2', 'args': ['HTML5 W3C'],
              'scope': 'specification description',
              'kumascript': '{{Spec2("HTML5 W3C")}}',
              'expected_scopes': 'specification maturity'}),
            ('unknown_spec', 19, 41, {'key': 'HTML5 W3C'})]
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
        kname = 'experimental_inline'
        issue = (
            'unexpected_kumascript', 102, 129,
            {'args': [], 'kumascript': '{{%s}}' % kname,
             'name': kname, 'scope': 'specification description',
             'expected_scopes': 'compatibility feature'})
        self.assert_specdesc(html, expected, [issue])
