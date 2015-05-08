# coding: utf-8
"""Test mdn.scrape."""
from __future__ import unicode_literals
from datetime import date
from json import dumps

from mdn.models import FeaturePage
from mdn.scrape import (
    date_to_iso, end_of_line, page_grammar, range_error_to_html, scrape_page,
    scrape_feature_page, slugify, PageVisitor, ScrapedViewFeature)
from webplatformcompat.models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)
from webplatformcompat.tests.base import TestCase


class TestGrammar(TestCase):
    def assert_other_h2(self, other_h2, expected_title):
        """Assert the title is extracted by rule other_h2"""
        parsed = page_grammar['other_h2'].parse(other_h2)
        capture = parsed.children[6]
        self.assertEqual(expected_title, capture.text)

    def test_other_h2_plain(self):
        other_h2 = "<h2 id=\"Summary\">Summary</h2>"
        expected_title = "Summary"
        self.assert_other_h2(other_h2, expected_title)

    def test_other_h2_code(self):
        other_h2 = "<h2 id=\"Summary\"><code>Summary</code></h2>"
        expected_title = "<code>Summary</code>"
        self.assert_other_h2(other_h2, expected_title)

    def assert_spec_h2(self, spec_h2, expected_attrs, expected_title):
        parsed = page_grammar['spec_h2'].parse(spec_h2)
        attrs = parsed.children[2]
        title = parsed.children[6]
        self.assertEqual(expected_attrs, attrs.text)
        self.assertEqual(expected_title, title.text)

    def test_spec_h2_expected(self):
        spec_h2 = '<h2 id="Specifications">Specifications</h2>'
        expected_attrs = 'id="Specifications"'
        expected_title = 'Specifications'
        self.assert_spec_h2(spec_h2, expected_attrs, expected_title)

    def test_spec_h2_browser_compat(self):
        spec_h2 = (
            '<h2 id="Browser_compatibility" name="Browser_compatibility">'
            'Specifications</h2>')
        expected_attrs = (
            'id="Browser_compatibility" name="Browser_compatibility"')
        expected_title = "Specifications"
        self.assert_spec_h2(spec_h2, expected_attrs, expected_title)

    def assert_spec_headers(self, spec_headers, expected_tag, expected_title):
        parsed = page_grammar['spec_headers'].parse(spec_headers)
        th_elems = parsed.children[2]
        col1 = th_elems.children[0]
        tag = col1.children[0]
        title = col1.children[2]
        self.assertEqual(expected_tag, tag.text)
        self.assertEqual(expected_title, title.text)

    def test_spec_headers_scoped(self):
        # Most common version
        spec_headers = """<tr>
          <th scope="col">Specification</th>
          <th scope="col">Status</th>
          <th scope="col">Comment</th>
        </tr>"""
        expected_tag = '<th scope="col">'
        expected_title = 'Specification'
        self.assert_spec_headers(spec_headers, expected_tag, expected_title)

    def test_spec_headers_unscoped(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        spec_headers = """<tr>
          <th>Specification</th>
          <th>Status</th>
          <th>Comment</th>
        </tr>"""
        expected_tag = '<th>'
        expected_title = 'Specification'
        self.assert_spec_headers(spec_headers, expected_tag, expected_title)

    def test_spec_headers_strong(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
        spec_headers = """<tr>
          <th scope="col"><strong>Specification</strong></th>
          <th scope="col"><strong>Status</strong></th>
          <th scope="col"><strong>Comment</strong></th>
        </tr>"""
        expected_tag = '<th scope="col">'
        expected_title = '<strong>Specification</strong>'
        self.assert_spec_headers(spec_headers, expected_tag, expected_title)

    def assert_spec_row(self, spec_row, expected_tag):
        parsed = page_grammar['spec_row'].parse(spec_row)
        tr = parsed.children[0]
        self.assertEqual(expected_tag, tr.text)

    def test_spec_row_standard(self):
        spec_row = """<tr>
          <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',
            'background-size')}}</td>
          <td>{{Spec2('CSS3 Backgrounds')}}</td>
          <td></td>
        </tr>"""
        expected_tag = '<tr>'
        self.assert_spec_row(spec_row, expected_tag)

    def test_spec_row_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        spec_row = """<tr style="vertical-align: top;">
          <td>{{ SpecName('CSS2.1', "cascade.html#value-def-inherit",
            "inherit") }}</td>
          <td>{{ Spec2('CSS2.1') }}</td>
          <td>Initial definition</td>
        </tr>"""
        expected_tag = '<tr style="vertical-align: top;">'
        self.assert_spec_row(spec_row, expected_tag)

    def assert_specname_td(self, specname_td, expected_tag):
        parsed = page_grammar['specname_td'].parse(specname_td)
        tr = parsed.children[0]
        self.assertEqual(expected_tag, tr.text)

    def test_specname_td_standard(self):
        specname_td = """<td>{{SpecName('CSS3 Backgrounds', '#the-background-size',
            'background-size')}}</td>"""
        expected_tag = '<td>'
        self.assert_specname_td(specname_td, expected_tag)

    def test_specname_td_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        specname_td = """<td style="vertical-align: top;">{{ SpecName('CSS2.1',
            "cascade.html#value-def-inherit", "inherit") }}</td>"""
        expected_tag = '<td style="vertical-align: top;">'
        self.assert_specname_td(specname_td, expected_tag)

    def assert_spec2_td(self, spec2_td, expected_tag):
        parsed = page_grammar['spec2_td'].parse(spec2_td)
        tr = parsed.children[0]
        self.assertEqual(expected_tag, tr.text)

    def test_spec2_td_standard(self):
        spec2_td = "<td>{{Spec2('CSS3 Backgrounds')}}</td>"
        expected_tag = '<td>'
        self.assert_spec2_td(spec2_td, expected_tag)

    def test_spec2_td_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        spec2_td = """<td style="vertical-align: top;">
            {{ Spec2("CSS2.1") }}
        </td>"""
        expected_tag = '<td style="vertical-align: top;">'
        self.assert_spec2_td(spec2_td, expected_tag)

    def assert_specdesc_td(self, specdesc_td, expected_tag, expected_desc):
        parsed = page_grammar['specdesc_td'].parse(specdesc_td)
        tag = parsed.children[0]
        self.assertEqual(expected_tag, tag.text)
        capture = parsed.children[2]
        self.assertEqual(expected_desc, capture.text)

    def test_specdesc_td_empty(self):
        specdesc_td = '<td></td>'
        expected_tag = '<td>'
        expected_desc = ''
        self.assert_specdesc_td(specdesc_td, expected_tag, expected_desc)

    def test_specdesc_td_plain_text(self):
        specdesc_td = '<td>Plain Text</td>'
        expected_tag = '<td>'
        expected_desc = 'Plain Text'
        self.assert_specdesc_td(specdesc_td, expected_tag, expected_desc)

    def test_specdesc_td_html(self):
        specdesc_td = "<td>Defines <code>right</code> as animatable.</td>"
        expected_tag = '<td>'
        expected_desc = 'Defines <code>right</code> as animatable.'
        self.assert_specdesc_td(specdesc_td, expected_tag, expected_desc)

    def test_specdesc_td_styled(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/inherit
        specdesc_td = """<td style=\"vertical-align: top;\">
            Initial definition.
        </td>"""
        expected_tag = '<td style="vertical-align: top;">'
        expected_desc = "Initial definition.\n        "
        self.assert_specdesc_td(specdesc_td, expected_tag, expected_desc)

    def assert_compat_headers(
            self, headers, expected_feature, expected_browsers):
        parsed = page_grammar['compat_headers'].parse(headers)
        feature = parsed.children[2]
        browsers = parsed.children[4]
        self.assertEqual(expected_feature, feature.text)
        self.assertEqual(expected_browsers, browsers.text)

    def test_compat_headers_standard(self):
        headers = "<tr><th>Feature</th><th>Firefox</th></tr>"
        expected_feature = '<th>Feature</th>'
        expected_browsers = '<th>Firefox</th>'
        self.assert_compat_headers(
            headers, expected_feature, expected_browsers)

    def test_compat_headers_strong(self):
        headers = (
            "<tr><th><strong>Feature</strong></th>"
            "<th><strong>Firefox</strong></th></tr>")
        expected_feature = '<th><strong>Feature</strong></th>'
        expected_browsers = '<th><strong>Firefox</strong></th>'
        self.assert_compat_headers(
            headers, expected_feature, expected_browsers)

    def assert_cell_version(self, text, version, eng_version=None):
        match = page_grammar['cell_version'].parse(text).match.groupdict()
        expected = {'version': version, 'eng_version': eng_version}
        self.assertEqual(expected, match)

    def test_cell_version_number(self):
        self.assert_cell_version("1", version="1")

    def test_cell_version_number_dotted(self):
        self.assert_cell_version("1.0", version="1.0")

    def test_cell_version_number_spaces(self):
        self.assert_cell_version("1 ", version="1")

    def test_cell_version_number_dotted_spaces(self):
        self.assert_cell_version("1.0\n\t", version="1.0")

    def test_cell_version_number_with_engine(self):
        self.assert_cell_version("1.0 (85)", version="1.0", eng_version="85")

    def test_cell_version_number_with_dotted_engine(self):
        self.assert_cell_version(
            "5.0 (532.5)", version="5.0", eng_version="532.5")


class ScrapeTestCase(TestCase):
    """Fixtures for scraping tests."""
    longMessage = True

    # Based on:
    # https://developer.mozilla.org/en-US/docs/Web/CSS/background-size?raw
    # but significantly reduced.
    sample_spec_row = """\
<tr>
   <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',\
 'background-size')}}</td>
   <td>{{Spec2('CSS3 Backgrounds')}}</td>
   <td></td>
  </tr>"""

    sample_spec_section = """\
<h2 id="Specifications" name="Specifications">Specifications</h2>
<table class="standard-table">
 <thead>
  <tr>
   <th scope="col">Specification</th>
   <th scope="col">Status</th>
   <th scope="col">Comment</th>
  </tr>
 </thead>
 <tbody>
  %s
 </tbody>
</table>
""" % sample_spec_row

    sample_page = """\
<div>{{CSSREF}}</div>
<h2 id="Summary">Summary</h2>
<p>This represents all the other page content</p>
<p>{{cssbox("background-size")}}</p>
%s
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{CompatibilityTable}}</div>
<div id="compat-desktop">
 <table class="compat-table">
  <tbody>
   <tr>
     <th>Feature</th><th>Chrome</th>
     <th>Firefox (Gecko)</th></tr>
   <tr>
     <td>Basic support</td><td>1.0</td>
     <td>{{CompatGeckoDesktop("1")}}</td>
   </tr>
  </tbody>
 </table>
</div>
<h2 id="See_also">See also</h2>
<ul>
 <li>{{CSS_Reference:Position}}</li>
</ul>""" % sample_spec_section
    _instance_specs = {
        (Maturity, 'CR'): {'name': '{"en": "Candidate Recommendation"}'},
        (Specification, 'css3_backgrounds'): {
            '_req': {'maturity': (Maturity, 'CR')},
            'mdn_key': 'CSS3 Backgrounds',
            'name': (
                '{"en": "CSS Backgrounds and Borders Module Level&nbsp;3"}'),
            'uri': '{"en": "http://dev.w3.org/csswg/css3-background/"}'},
        (Section, 'background-size'): {
            '_req': {'specification': (Specification, 'css3_backgrounds')},
            'subpath': '{"en": "#the-background-size"}'},
        (Feature, 'web'): {'name': '{"en": "Web"}'},
        (Feature, 'web-css'): {
            '_req': {'parent': (Feature, 'web')}, 'name': '{"en": "CSS"}'},
        (Feature, 'web-css-background-size'): {
            '_req': {'parent': (Feature, 'web-css')},
            'name': '{"zxx": "background-size"}'},
        (Feature, 'web-css-background-size-basic_support'): {
            '_req': {'parent': (Feature, 'web-css-background-size')},
            'name': '{"en": "Basic support"}'},
        (Browser, 'chrome'): {'name': '{"en": "Chrome"}'},
        (Browser, 'firefox'): {'name': '{"en": "Firefox"}'},
        (Version, ('chrome', '1.0')): {},
        (Version, ('firefox', '')): {},
        (Version, ('firefox', '1.0')): {},
    }

    def get_instance(self, model_cls, slug):
        """Get a test fixture instance, creating on first access."""
        instance_key = (model_cls, slug)
        if not hasattr(self, '_instances'):
            self._instances = {}
        if instance_key not in self._instances:
            attrs = self._instance_specs[instance_key].copy()
            req = attrs.pop('_req', {})
            if model_cls == Version:
                browser_slug, version = slug
                attrs['browser'] = self.get_instance(Browser, browser_slug)
                attrs['version'] = version
            elif model_cls == Section:
                attrs['name'] = '{"en": "%s"}' % slug
            else:
                attrs['slug'] = slug
            for req_name, (req_type, req_slug) in req.items():
                attrs[req_name] = self.get_instance(req_type, req_slug)
            self._instances[instance_key] = self.create(model_cls, **attrs)
        return self._instances[instance_key]


class TestEndOfLine(ScrapeTestCase):
    def setUp(self):
        self.text = """\
    This is some sample text.
  Each line is 30 characters,
  when you count the newline:
12345678911234567892123456789"""

    def test_middle_of_text(self):
        end = end_of_line(self.text, 50)
        self.assertEqual(59, end)

    def test_end_of_text(self):
        end = end_of_line(self.text, len(self.text) - 2)
        self.assertEqual(len(self.text), end)


class TestPageVisitor(ScrapeTestCase):
    def setUp(self):
        feature = self.get_instance(Feature, 'web-css-background-size')
        self.visitor = PageVisitor(feature)

    def test_doc_no_spec(self):
        doc = '<h2 id="Specless">No specs here</h2>'
        parsed = page_grammar['doc'].parse(doc)
        doc_parts = self.visitor.visit(parsed)
        expected = {
            'locale': 'en', 'specs': [], 'issues': [], 'errors': [],
            'compat': [], 'footnotes': None}
        self.assertEqual(expected, doc_parts)
        self.assertEqual([], self.visitor.issues)
        self.assertEqual([], self.visitor.errors)

    def assert_last_section(self, last_section, errors):
        parsed = page_grammar['last_section'].parse(last_section)
        self.visitor.visit(parsed)
        self.assertEqual([], self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_last_section_ignored(self):
        last_section = (
            "<h2 id=\"summary\">Summary</h2>\n"
            "<p>In summary, this section is ignored.</p>\n")
        self.assert_last_section(last_section, [])

    def test_last_section_invalid(self):
        last_section = (
            "<h2 id=\"specifications\">Specifications</h2>\n"
            "<p><em>TODO:</em> Specs go here</p>")
        errors = [
            (44, 79,
             "Section <h2>Specifications</h2> was not parsed. The parser"
             " failed on rule \"spec_table\", but the real cause may be"
             " unexpected content after this position. Definition:",
             'spec_table = "<table class="standard-table">" _ spec_head'
             ' _ spec_body _ "</table>" _')]
        self.assert_last_section(last_section, errors)

    def test_last_section_invalid_after_other_errors(self):
        self.visitor.errors = [(0, 0, 'An existing error')]
        last_section = (
            "<h2 id=\"specifications\">Specifications</h2>\n"
            "<p><em>TODO:</em> Specs go here</p>")
        errors = [
            (0, 0, 'An existing error'),
            (44, 79,
             "Section <h2>Specifications</h2> was not parsed. The parser"
             " failed on rule \"spec_table\", but the real cause is"
             " probably earlier issues. Definition:",
             'spec_table = "<table class="standard-table">" _ spec_head'
             ' _ spec_body _ "</table>" _')]
        self.assert_last_section(last_section, errors)

    def test_last_section_valid_specifications(self):
        errors = [
            (0, 65,
             "Section Specifications not parsed, probably due to earlier"
             " errors.")]
        self.assert_last_section(self.sample_spec_section, errors)

    def assert_spec_h2(self, spec_h2, expected_issues):
        parsed = page_grammar['spec_h2'].parse(spec_h2)
        self.visitor.visit(parsed)
        self.assertEqual(expected_issues, self.visitor.issues)

    def test_spec_h2_expected(self):
        self.assert_spec_h2(
            '<h2 name="Specifications" id="Specifications">'
            'Specifications</h2>', [])

    def test_spec_h2_discards_extra(self):
        self.assert_spec_h2(
            '<h2 id="Specifications" name="Specifications" extra="crazy">'
            'Specifications</h2>', [])

    def test_spec_h2_browser_compat(self):
        # Common bug from copying from Browser Compatibility section
        self.assert_spec_h2(
            '<h2 id="Browser_compatibility" name="Browser_compatibility">'
            'Specifications</h2>',
            [(4, 31,
              ('In Specifications section, expected <h2 id="Specifications">,'
               ' actual id="Browser_compatibility"')),
             (31, 59,
              ('In Specifications section, expected <h2'
               ' name="Specifications"> or no name attribute, actual'
               ' name="Browser_compatibility"'))])

    def assert_spec_row(self, spec_table, expected_specs, errors):
        parsed = page_grammar['spec_row'].parse(spec_table)
        self.visitor.visit(parsed)
        self.assertEqual(expected_specs, self.visitor.specs)
        self.assertEqual(errors, self.visitor.errors)

    def test_spec_row_mismatch(self):
        spec_row = '''\
<tr>
  <td>{{ SpecName('CSS3 UI', '#cursor', 'cursor') }}</td>
  <td>{{ Spec2('CSS3 Basic UI') }}</td>
  <td>Addition of several keywords and the positioning syntax for\
 <code>url()</code>.</td>
</tr>'''
        expected_specs = [{
            'section.note': (
                'Addition of several keywords and the positioning syntax for'
                ' <code>url()</code>.'),
            'section.subpath': '#cursor',
            'section.name': 'cursor',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': None}]
        errors = [
            (7, 62, 'Unknown Specification "CSS3 UI"'),
            (0, 199,
             'SpecName(CSS3 Basic UI, ...) does not match Spec2(CSS3 UI)')]
        self.assert_spec_row(spec_row, expected_specs, errors)

    def test_spec_row_specname_commas_in_link(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element
        #  /Heading_Elements
        spec_row = '''\
<tr>
  <td>{{SpecName('HTML WHATWG',\
 'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements',\
 '&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;, and &lt;h6&gt;'\
 )}}</td>
  <td>{{Spec2('HTML WHATWG')}}</td>
  <td>&nbsp;</td>
</tr>'''
        expected_specs = [{
            'section.note': '',
            'section.subpath': (
                'sections.html#the-h1,-h2,-h3,-h4,-h5,-and-h6-elements'),
            'section.name': (
                '&lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;,'
                ' and &lt;h6&gt;'),
            'specification.mdn_key': 'HTML WHATWG',
            'section.id': None,
            'specification.id': None}]
        errors = [(7, 179, 'Unknown Specification "HTML WHATWG"')]
        self.assert_spec_row(spec_row, expected_specs, errors)

    def test_spec_row_no_thead(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AudioContext
        spec_row = '''\
<tr>
  <td>{{SpecName('Web Audio API', '#the-audiocontext-interface',\
 'AudioContext')}}</td>
  <td>{{Spec2('Web Audio API')}}</td>
  <td>&nbsp;</td>
</tr>'''
        expected_specs = [{
            'section.note': '',
            'section.subpath': '#the-audiocontext-interface',
            'section.name': 'AudioContext',
            'specification.mdn_key': 'Web Audio API',
            'section.id': None,
            'specification.id': None}]
        errors = [(7, 92, 'Unknown Specification "Web Audio API"')]
        self.assert_spec_row(spec_row, expected_specs, errors)

    def test_spec_row_known_spec(self):
        spec = self.get_instance(Specification, 'css3_backgrounds')
        self.create(Section, specification=spec)
        expected_specs = [{
            'section.note': '',
            'section.subpath': '#the-background-size',
            'section.name': 'background-size',
            'specification.mdn_key': 'CSS3 Backgrounds',
            'section.id': None,
            'specification.id': spec.id}]
        self.assert_spec_row(self.sample_spec_row, expected_specs, [])

    def test_spec_row_known_spec_and_section(self):
        section = self.get_instance(Section, 'background-size')
        spec = section.specification
        expected_specs = [{
            'section.note': '',
            'section.subpath': '#the-background-size',
            'section.name': 'background-size',
            'specification.mdn_key': 'CSS3 Backgrounds',
            'section.id': section.id,
            'specification.id': spec.id}]
        self.assert_spec_row(self.sample_spec_row, expected_specs, [])

    def assert_specname_td(self, specname_td, expected):
        parsed = page_grammar['specname_td'].parse(specname_td)
        specname = self.visitor.visit(parsed)
        self.assertEqual(expected, specname)

    def test_specname_td_3_arg(self):
        # Common usage of SpecName
        spec = self.get_instance(Specification, 'css3_backgrounds')
        specname_td = (
            '<td>{{SpecName("CSS3 Backgrounds", "#subpath", "Name")}}</td>')
        expected = ('CSS3 Backgrounds', spec.id, "#subpath", "Name")
        self.assert_specname_td(specname_td, expected)

    def test_specname_td_1_arg(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent
        specname_td = '<td>{{SpecName("Device Orientation")}}</td>'
        expected = ("Device Orientation", None, '', '')
        self.assert_specname_td(specname_td, expected)

    def assert_compat_section(self, compat_section, compat, footnotes, errors):
        parsed = page_grammar['compat_section'].parse(compat_section)
        self.visitor.visit(parsed)
        self.assertEqual(compat, self.visitor.compat)
        self.assertEqual(footnotes, self.visitor.footnotes)
        self.assertEqual([], self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_compat_section_minimal(self):
        compat_section = """\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{CompatibilityTable}}</div>
<div id="compat-desktop">
 <table class="compat-table">
  <tbody>
   <tr><th>Feature</th><th>Firefox (Gecko)</th></tr>
   <tr><td>Basic support</td><td>{{CompatGeckoDesktop("1")}}</td></tr>
  </tbody>
 </table>
</div>
"""
        expected_compat = [{
            'name': u'desktop',
            'browsers': [{
                'id': '_Firefox (Gecko)', 'name': 'Firefox',
                'slug': '_Firefox (Gecko)'}],
            'versions': [{
                'browser': '_Firefox (Gecko)', 'id': '_Firefox-1.0',
                'version': '1.0'}],
            'features': [{
                'id': '_basic support', 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'feature': '_basic support',
                'id': '__basic support-_Firefox-1.0',
                'support': 'yes', 'version': '_Firefox-1.0'}]}]
        errors = [(185, 200, 'Unknown Browser "Firefox (Gecko)"')]
        self.assert_compat_section(compat_section, expected_compat, {}, errors)

    def test_compat_section_footnote(self):
        compat_section = """\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{CompatibilityTable}}</div>
<div id="compat-desktop">
 <table class="compat-table">
  <tbody>
   <tr><th>Feature</th><th>Chrome</th></tr>
   <tr><td>Basic support</td><td>1.0 [1]</td></tr>
  </tbody>
 </table>
</div>
<p>[1] This is a footnote.</p>
"""
        expected_compat = [{
            'name': u'desktop',
            'browsers': [{
                'id': '_Chrome', 'name': 'Chrome', 'slug': '_Chrome'}],
            'versions': [{
                'browser': '_Chrome', 'id': '_Chrome-1.0', 'version': '1.0'}],
            'features': [{
                'id': '_basic support', 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'feature': '_basic support',
                'id': '__basic support-_Chrome-1.0',
                'support': 'yes', 'version': '_Chrome-1.0',
                'footnote': 'This is a footnote.',
                'footnote_id': ('1', 239, 242)}]}]
        errors = [(185, 191, 'Unknown Browser "Chrome"')]
        self.assert_compat_section(compat_section, expected_compat, {}, errors)

    def test_compat_section_footnote_mismatch(self):
        compat_section = """\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{CompatibilityTable}}</div>
<div id="compat-desktop">
 <table class="compat-table">
  <tbody>
   <tr><th>Feature</th><th>Chrome</th></tr>
   <tr><td>Basic support</td><td>3.0 [1]</td></tr>
  </tbody>
 </table>
</div>
<p>[2] Oops, footnote ID is wrong.</p>
"""
        expected_compat = [{
            'name': u'desktop',
            'browsers': [{
                'id': '_Chrome', 'name': 'Chrome', 'slug': '_Chrome'}],
            'versions': [{
                'browser': '_Chrome', 'id': '_Chrome-3.0', 'version': '3.0'}],
            'features': [{
                'id': '_basic support', 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'feature': '_basic support',
                'id': '__basic support-_Chrome-3.0',
                'support': 'yes', 'version': '_Chrome-3.0',
                'footnote_id': ('1', 239, 242)}]}]
        footnotes = {'2': ('Oops, footnote ID is wrong.', 281, 320)}
        errors = [
            (185, 191, 'Unknown Browser "Chrome"'),
            (239, 242, 'Footnote [1] not found'),
            (281, 320, 'Footnote [2] not used')]
        self.assert_compat_section(
            compat_section, expected_compat, footnotes, errors)

    def assert_compat_headers(self, compat_headers, expected, issues, errors):
        parsed = page_grammar['compat_headers'].parse(compat_headers)
        headers = self.visitor.visit(parsed)
        self.assertEqual(expected, headers)
        self.assertEqual(issues, self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_compat_headers_unknown_browser(self):
        compat_headers = "<tr><th>Feature</th><th>Firefox</th></tr>"
        expected = [{'slug': '_Firefox', 'name': 'Firefox', 'id': "_Firefox"}]
        errors = [(24, 31, 'Unknown Browser "Firefox"')]
        self.assert_compat_headers(compat_headers, expected, [], errors)

    def test_compat_headers_known_browser(self):
        firefox = self.get_instance(Browser, 'firefox')
        compat_headers = "<tr><th>Feature</th><th>Firefox</th></tr>"
        expected = [{'slug': 'firefox', 'name': 'Firefox', 'id': firefox.id}]
        self.assert_compat_headers(compat_headers, expected, [], [])

    def test_compat_headers_strong(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
        firefox = self.get_instance(Browser, 'firefox')
        compat_headers = (
            "<tr><th><strong>Feature</strong></th>"
            "<th><strong>Firefox</strong></th></tr>")
        expected = [{'slug': 'firefox', 'name': 'Firefox', 'id': firefox.id}]
        self.assert_compat_headers(compat_headers, expected, [], [])

    def test_compat_headers_wrong_first_column_header(self):
        # All known pages use "Feature" for first column, but be ready
        firefox = self.get_instance(Browser, 'firefox')
        compat_headers = (
            "<tr><th><strong>Features</strong></th>"
            "<th><strong>Firefox</strong></th></tr>")
        expected = [{'slug': 'firefox', 'name': 'Firefox', 'id': firefox.id}]
        issues = [(16, 24, 'Expected header "Feature"')]
        self.assert_compat_headers(compat_headers, expected, issues, [])

    def test_compat_headers_with_colspan(self):
        # https://developer.mozilla.org/en-US/Web/CSS/background-size
        compat_headers = (
            "<tr><th>Feature</th>"
            "<th colspan=\"3\">Safari (WebKit)</th></tr>")
        expected = [{
            'slug': '_Safari (WebKit)',
            'name': 'Safari',
            'id': '_Safari (WebKit)',
            'colspan': '3'
        }]
        errors = [(36, 51, 'Unknown Browser "Safari (WebKit)"')]
        self.assert_compat_headers(compat_headers, expected, [], errors)

    def assert_compat_row_cell(self, row_cell, expected_cell, issues):
        parsed = page_grammar['compat_row_cell'].parse(row_cell)
        cell = self.visitor.visit(parsed)
        self.assertEqual(expected_cell, cell)
        self.assertEqual(issues, self.visitor.issues)

    def test_compat_row_cell_feature_with_rowspan(self):
        row_cell = '<td rowspan="2">Some Feature</td>'
        expected_cell = [
            {'type': 'td', 'rowspan': '2', 'start': 0, 'end': 16},
            {'type': 'text', 'content': 'Some Feature', 'start': 16,
             'end': 28}]
        self.assert_compat_row_cell(row_cell, expected_cell, [])

    def test_compat_row_cell_feature_with_unknown_attr(self):
        row_cell = '<td class="freaky">Freaky Feature</td>'
        expected_cell = [
            {'type': 'td', 'start': 0, 'end': 19},
            {'type': 'text', 'content': 'Freaky Feature', 'start': 19,
             'end': 33}]
        issues = [(4, 18, 'Unexpected attribute <td class="freaky">')]
        self.assert_compat_row_cell(row_cell, expected_cell, issues)

    def test_compat_row_cell_break(self):
        row_cell = '<td>Multi-line<br/>feature</td>'
        expected_cell = [
            {'type': 'td', 'start': 0, 'end': 4},
            {'type': 'text', 'content': 'Multi-line', 'start': 4, 'end': 14},
            {'type': 'break', 'start': 14, 'end': 19},
            {'type': 'text', 'content': 'feature', 'start': 19, 'end': 26},
        ]
        self.assert_compat_row_cell(row_cell, expected_cell, [])

    def test_compat_row_cell_kumascript(self):
        row_cell = '<td>EXP {{experimental_inline}} FEATURE</td>'
        expected_cell = [
            {'type': 'td', 'start': 0, 'end': 4},
            {'type': 'text', 'content': 'EXP', 'start': 4, 'end': 8},
            {'type': 'kumascript', 'name': 'experimental_inline', 'args': [],
             'start': 8, 'end': 32},
            {'type': 'text', 'content': 'FEATURE', 'start': 32, 'end': 39},
        ]
        self.assert_compat_row_cell(row_cell, expected_cell, [])

    def test_compat_row_cell_code_block(self):
        row_cell = '<td><code>canonical</code></td>'
        expected_cell = [
            {'type': 'td', 'start': 0, 'end': 4},
            {'type': 'code_block', 'content': 'canonical', 'start': 4,
             'end': 26},
        ]
        self.assert_compat_row_cell(row_cell, expected_cell, [])

    def assert_cell_to_feature(
            self, contents, expected_feature, issues, errors):
        row_cell = "<td>%s</td>" % contents
        parsed = page_grammar['compat_row_cell'].parse(row_cell)
        cell = self.visitor.visit(parsed)
        feature = self.visitor.cell_to_feature(cell)
        self.assertEqual(expected_feature, feature)
        self.assertEqual(issues, self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_cell_to_feature_remove_whitespace(self):
        cell = (
            ' Support for<br>\n     <code>contain</code> and'
            ' <code>cover</code> ')
        expected_feature = {
            'id': '_support for contain and cover',
            'name': 'Support for <code>contain</code> and <code>cover</code>',
            'slug': 'web-css-background-size_support_for_contain_and_co',
        }
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_code_sequence(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/display
        cell = (
            '<code>none</code>, <code>inline</code> and'
            ' <code>block</code>')
        expected_feature = {
            'id': '_none, inline and block',
            'name': (
                '<code>none</code>, <code>inline</code> and'
                ' <code>block</code>'),
            'slug': 'web-css-background-size_none_inline_and_block'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_canonical(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/display
        cell = '<code>list-item</code>'
        expected_feature = {
            'id': '_list-item', 'name': 'list-item', 'canonical': True,
            'slug': 'web-css-background-size_list-item'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_canonical_match(self):
        feature = self.create(
            Feature, parent=self.visitor.feature,
            name={'zxx': 'list-item'}, slug='slug-list-item')
        cell = '<code>list-item</code>'
        expected_feature = {
            'id': feature.id, 'name': 'list-item', 'slug': 'slug-list-item',
            'canonical': True,
        }
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_ks_experimental(self):
        cell = '<code>grid</code> {{experimental_inline}}'
        expected_feature = {
            'id': '_grid', 'name': 'grid', 'canonical': True,
            'experimental': True, 'slug': 'web-css-background-size_grid'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_ks_non_standard_inline(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AnimationEvent
        cell = '<code>initAnimationEvent()</code> {{non-standard_inline}}'
        expected_feature = {
            'id': '_initanimationevent()', 'name': 'initAnimationEvent()',
            'canonical': True, 'standardized': False,
            'slug': 'web-css-background-size_initanimationevent_'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_ks_deprecated_inline(self):
        cell = '<code>initAnimationEvent()</code> {{deprecated_inline}}'
        expected_feature = {
            'id': '_initanimationevent()', 'name': 'initAnimationEvent()',
            'canonical': True, 'obsolete': True,
            'slug': 'web-css-background-size_initanimationevent_'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_ks_htmlelement(self):
        cell = '{{ HTMLElement("progress") }}'
        expected_feature = {
            'id': '_&lt;progress&gt;', 'name': '&lt;progress&gt;',
            'canonical': True,
            'slug': 'web-css-background-size_lt_progress_gt_',
        }
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_ks_domxref(self):
        cell = '{{domxref("DeviceProximityEvent")}}'
        expected_feature = {
            'id': '_deviceproximityevent', 'name': 'DeviceProximityEvent',
            'slug': 'web-css-background-size_deviceproximityevent',
        }
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_unknown_kumascript(self):
        cell = 'feature foo {{bar}}'
        expected_feature = {
            'id': '_feature foo', 'name': 'feature foo',
            'slug': 'web-css-background-size_feature_foo'}
        errors = [(16, 23, 'Unknown kumascript function bar')]
        self.assert_cell_to_feature(cell, expected_feature, [], errors)

    def test_cell_to_feature_unknown_kumascript_with_args(self):
        cell = 'foo {{bar("baz")}}'
        expected_feature = {
            'id': '_foo', 'name': 'foo', 'slug': 'web-css-background-size_foo'}
        errors = [(8, 22, 'Unknown kumascript function bar(baz)')]
        self.assert_cell_to_feature(cell, expected_feature, [], errors)

    def test_cell_to_feature_nonascii_name(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant
        cell = '<code>ß</code> → <code>SS</code>'
        expected_feature = {
            'id': '_\xdf \u2192 ss',
            'name': '<code>\xdf</code> \u2192 <code>SS</code>',
            'slug': 'web-css-background-size_ss'}
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_footnote(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-align
        cell = 'Block alignment values [1] {{not_standard_inline}}'
        expected_feature = {
            'id': '_block alignment values', 'name': 'Block alignment values',
            'standardized': False,
            'slug': 'web-css-background-size_block_alignment_values'}
        errors = [(27, 31, "Footnotes are not allowed on features")]
        self.assert_cell_to_feature(cell, expected_feature, [], errors)

    def test_cell_to_feature_digit(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/transform
        cell = '3D Support'
        expected_feature = {
            'id': '_3d support', 'name': '3D Support',
            'slug': 'web-css-background-size_3d_support'
        }
        self.assert_cell_to_feature(cell, expected_feature, [], [])

    def test_cell_to_feature_unknown_item(self):
        bad_cell = [{'type': 'td'}, {'type': 'other'}]
        self.assertRaises(ValueError, self.visitor.cell_to_feature, bad_cell)

    def assert_cell_to_support_full(
            self, row_cell, feature_rep, browser_rep, expected_versions,
            expected_supports, issues, errors):
        """Complete test of cell_to_support."""
        parsed = page_grammar['compat_row_cell'].parse(row_cell)
        cell = self.visitor.visit(parsed)
        versions, supports = self.visitor.cell_to_support(
            cell, feature_rep, browser_rep)
        self.assertEqual(expected_versions, versions)
        self.assertEqual(expected_supports, supports)
        self.assertEqual(issues, self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def get_feature_rep(self, feature):
        """Create the visitor representation of a feature"""
        return {
            'id': feature.id, 'name': feature.name['en'], 'slug': feature.slug}

    def get_browser_rep(self, browser):
        """Create the visitor representation of a browser"""
        return {
            'id': browser.id, 'name': browser.name['en'], 'slug': browser.slug}

    def test_cell_to_support_matched_version(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')

        row_cell = "<td>1.0</td>"
        feature_rep = self.get_feature_rep(feature)
        browser_rep = self.get_browser_rep(browser)
        expected_versions = [{
            'id': version.id, 'version': version.version,
            'browser': browser.id}]
        expected_supports = [{
            'id': '_%s-%s' % (feature.id, version.id),
            'support': "yes", 'version': version.id, 'feature': feature.id}]
        self.assert_cell_to_support_full(
            row_cell, feature_rep, browser_rep, expected_versions,
            expected_supports, [], [])

    def test_cell_to_support_unknown_version(self):
        browser = self.get_instance(Browser, 'firefox')

        row_cell = "<td>1.0</td>"
        feature_rep = {'id': '_feature', 'name': 'feature', 'slug': 'fslug'}
        browser_rep = self.get_browser_rep(browser)
        expected_versions = [{
            'id': '_Firefox-1.0', 'version': '1.0', 'browser': browser.id}]
        expected_supports = [{
            'id': '__feature-_Firefox-1.0', 'support': "yes",
            'version': '_Firefox-1.0', 'feature': '_feature'}]
        errors = [
            (4, 7,
             'Unknown version "1.0" for browser "Firefox" (id %d, slug "%s")'
             % (browser.id, 'firefox'))]
        self.assert_cell_to_support_full(
            row_cell, feature_rep, browser_rep, expected_versions,
            expected_supports, [], errors)

    def test_cell_to_support_matched_support(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        support = self.create(Support, version=version, feature=feature)

        row_cell = "<td>1.0</td>"
        feature_rep = self.get_feature_rep(feature)
        browser_rep = self.get_browser_rep(browser)
        expected_versions = [{
            'id': version.id, 'version': version.version,
            'browser': browser.id}]
        expected_supports = [{
            'id': support.id, 'support': "yes", 'version': version.id,
            'feature': feature.id}]
        self.assert_cell_to_support_full(
            row_cell, feature_rep, browser_rep, expected_versions,
            expected_supports, [], [])

    def test_compat_row_cell_support_compatversionunknown_vmatch(self):
        version = self.get_instance(Version, ('firefox', ''))
        browser = version.browser
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')

        row_cell = "<td>{{CompatVersionUnknown}}</td>"
        feature_rep = self.get_feature_rep(feature)
        browser_rep = self.get_browser_rep(browser)
        expected_versions = [{
            'id': version.id, 'browser': browser.id, 'version': ''}]
        expected_supports = [{
            'id': '_%s-%s' % (feature.id, version.id),
            'version': version.id, 'feature': feature.id, 'support': "yes"}]
        self.assert_cell_to_support_full(
            row_cell, feature_rep, browser_rep, expected_versions,
            expected_supports, [], [])

    def assert_cell_to_support(
            self, contents, expected_versions=[], expected_supports=[],
            issues=[], errors=[]):
        """Test cell_to_support with helpful defaults."""
        row_cell = "<td>%s</td>" % contents
        feature_rep = {'id': '_feature', 'name': 'feature', 'slug': 'fslug'}
        browser_rep = {'id': '_browser', 'name': 'Browser', 'slug': 'browser'}
        for ev in expected_versions:
            assert 'id' not in ev
            assert 'browser' not in ev
            ev['id'] = '_%s-%s' % (browser_rep['name'], ev['version'])
            ev['browser'] = browser_rep['id']
        for i, es in enumerate(expected_supports):
            version = expected_versions[i]
            assert 'id' not in es
            assert 'version' not in es
            assert 'feature' not in es
            es['id'] = '_%s-%s' % (feature_rep['id'], version['id'])
            es['version'] = version['id']
            es['feature'] = feature_rep['id']
        self.assert_cell_to_support_full(
            row_cell, feature_rep, browser_rep,
            expected_versions, expected_supports, issues, errors)

    def test_cell_to_support_version(self):
        self.assert_cell_to_support(
            '1.0',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatno(self):
        self.assert_cell_to_support(
            '{{CompatNo}}',
            [{'version': ''}], [{'support': 'no'}])

    def test_cell_to_support_compatversionunknown(self):
        self.assert_cell_to_support(
            '{{CompatVersionUnknown}}',
            [{'version': ''}], [{'support': 'yes'}])

    def test_cell_to_support_compatunknown(self):
        self.assert_cell_to_support('{{CompatUnknown}}', [], [])

    def test_cell_to_support_compatgeckodesktop_10(self):
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("1")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckodesktop_8(self):
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("8.0")}}',
            [{'version': '8.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckodesktop_bad_text(self):
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("Yep")}}',
            errors=[(4, 33, 'Unknown Gecko version "Yep"')])

    def test_cell_to_support_compatgeckodesktop_bad_num(self):
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("1.1")}}',
            errors=[(4, 33, 'Unknown Gecko version "1.1"')])

    def test_cell_to_support_compatgeckofxos_7(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("7")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckofxos_7_version_1_0_1(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("7","1.0.1")}}',
            [{'version': '1.0.1'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckofxos_7_version_1_1(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("7","1.1")}}',
            [{'version': '1.1'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckofxos_range(self):
        versions = {'10': '1.0',
                    '24': '1.2',
                    '28': '1.3',
                    '29': '1.4',
                    '32': '2.0',
                    '34': '2.1',
                    '35': '2.2'
                    }
        for gversion, oversion in versions.items():
            self.assert_cell_to_support(
                '{{CompatGeckoFxOS("%s")}}' % gversion,
                [{'version': oversion}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckofxos_bad_gecko(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("9999999")}}',
            errors=[(4, 34, 'Unknown Gecko version "9999999"')])

    def test_cell_to_support_compatgeckofxos_bad_text(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("Yep")}}',
            errors=[(4, 30, 'Unknown Gecko version "Yep"')])

    def test_cell_to_support_compatgeckofxos_bad_version(self):
        self.assert_cell_to_support(
            '{{CompatGeckoFxOS("18","5.0")}}',
            errors=[(4, 35, (
                'Override "5.0" is invalid for Gecko version "18"'))])

    def test_cell_to_support_compatgeckomobile_1(self):
        self.assert_cell_to_support(
            '{{CompatGeckoMobile("1")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckomobile_1_11(self):
        self.assert_cell_to_support(
            '{{CompatGeckoMobile("1.11")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatgeckomobile_2(self):
        self.assert_cell_to_support(
            '{{CompatGeckoMobile("2")}}',
            [{'version': '4.0'}], [{'support': 'yes'}])

    def test_cell_to_support_compatandroid_3(self):
        self.assert_cell_to_support(
            '{{CompatAndroid("3.0")}}',
            [{'version': '3.0'}], [{'support': 'yes'}])

    def test_cell_to_support_unknown_kumascript(self):
        self.assert_cell_to_support(
            '{{UnknownKuma}}',
            errors=[(4, 19, "Unknown kumascript function UnknownKuma")])

    def test_cell_to_support_unknown_kumascript_args(self):
        self.assert_cell_to_support(
            '{{UnknownKuma("foo")}}',
            errors=[(4, 26, 'Unknown kumascript function UnknownKuma(foo)')])

    def test_cell_to_support_nested_p(self):
        self.assert_cell_to_support(
            '<p><p>4.0</p></p>',
            errors=[(7, 10, 'Nested <p> tags not supported')])

    def test_cell_to_support_with_prefix_and_break(self):
        self.assert_cell_to_support(
            ('{{CompatVersionUnknown}}{{property_prefix("-webkit")}}<br>\n'
             '   2.3'),
            [{'version': ''}, {'version': '2.3'}],
            [{'support': 'yes', 'prefix': '-webkit'}, {'support': 'yes'}])

    def test_cell_to_support_p_tags(self):
        self.assert_cell_to_support(
            '<p>4.0</p><p>32</p>',
            [{'version': '4.0'}, {'version': '32.0'}],
            [{'support': 'yes'}, {'support': 'yes'}])

    def test_cell_to_support_two_line_note(self):
        self.assert_cell_to_support(
            '18<br>\n(behind a pref) [1]',
            [{'version': '18.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 27, 30)}],
            errors=[(11, 27, 'Unknown support text "(behind a pref)"')])

    def test_cell_to_support_removed_in_gecko(self):
        self.assert_cell_to_support(
            ('{{ CompatGeckoMobile("6.0") }}<br>'
             'Removed in {{ CompatGeckoMobile("23.0") }}'),
            [{'version': '6.0'}, {'version': '23.0'}],
            [{'support': 'yes'}, {'support': 'no'}])

    def test_cell_to_support_removed_in_version(self):
        self.assert_cell_to_support(
            'Removed in 32',
            [{'version': '32.0'}], [{'support': 'no'}])

    def test_cell_to_support_unmatched_free_text(self):
        self.assert_cell_to_support(
            '32 (unprefixed)',
            [{'version': '32.0'}], [{'support': 'yes'}],
            errors=[(7, 19, 'Unknown support text "(unprefixed)"')])

    def test_cell_to_support_code_block(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/order
        self.assert_cell_to_support(
            '32 with alt name <code>foobar</code>',
            [{'version': '32.0'}], [{'support': 'yes'}],
            errors=[(7, 21, 'Unknown support text "with alt name"'),
                    (21, 40, 'Unknown support text <code>foobar</code>')])

    def test_cell_to_support_spaces(self):
        self.assert_cell_to_support('  ')

    def test_cell_to_support_prefix_plus_footnote(self):
        self.assert_cell_to_support(
            '18{{property_prefix("-webkit")}} [1]',
            [{'version': '18.0'}],
            [{'support': 'partial', 'prefix': '-webkit',
              'footnote_id': ('1', 37, 40)}])

    def test_cell_to_support_prefix_double_footnote(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/CSSSupportsRule
        self.assert_cell_to_support(
            '{{ CompatGeckoDesktop("17") }} [1][2]',
            [{'version': '17.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 35, 38)}],
            errors=[(38, 41, 'Only one footnote allowed.')])

    def test_cell_to_support_double_footnote_link_sup(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/flex
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("20.0")}} '
            '<sup><a href="#bc2">[2]</a><a href="#bc3">[3]</a></sup>',
            [{'version': '20.0'}],
            [{'support': 'yes', 'footnote_id': ('2', 35, 62)}],
            errors=[(62, 90, 'Only one footnote allowed.')])

    def test_cell_to_support_star_footnote(self):
        self.assert_cell_to_support(
            '{{CompatGeckoDesktop("20.0")}} [***]',
            [{'version': '20.0'}],
            [{'support': 'yes', 'footnote_id': ('3', 35, 40)}])

    def test_cell_to_support_nbsp(self):
        self.assert_cell_to_support(
            '15&nbsp;{{property_prefix("webkit")}}',
            [{'version': '15.0'}], [{'support': 'yes', 'prefix': 'webkit'}])

    def test_cell_to_support_unknown_item(self):
        feature = {'id': '_feature', 'name': 'feature', 'slug': 'feature_slug'}
        browser = {'id': '_browser', 'name': 'Browser', 'slug': 'browser'}
        bad_cell = [{'type': 'td'}, {'type': 'other'}]
        self.assertRaises(
            ValueError, self.visitor.cell_to_support, bad_cell, feature,
            browser)

    def assert_compat_body(self, compat_body, expected, errors):
        parsed = page_grammar['compat_body'].parse(compat_body)
        body = self.visitor.visit(parsed)
        self.assertEqual(expected, body)
        self.assertEqual([], self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_compat_body_success(self):
        chrome_10 = self.get_instance(Version, ('chrome', '1.0'))
        chrome = chrome_10.browser
        compat_body = """<tbody>
            <tr><th>Feature</th><th>Chrome</th></tr>
            <tr><td>Basic support</td><td>1.0</td></tr>
        </tbody>"""
        expected = {
            'browsers': [
                {'id': chrome.id, 'name': 'Chrome', 'slug': 'chrome'}],
            'features': [{
                'id': '_basic support', 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'feature': '_basic support',
                'id': '__basic support-%s' % chrome_10.id,
                'support': 'yes', 'version': chrome_10.id}],
            'versions': [{
                'browser': chrome.id, 'id': chrome_10.id, 'version': '1.0'}]}
        self.assert_compat_body(compat_body, expected, [])

    def test_compat_body_extra_feature_column(self):
        # https://developer.mozilla.org/en-US/docs/Web/JavaScript/
        # Reference/Global_Objects/WeakSet, March 2015
        chrome_10 = self.get_instance(Version, ('chrome', '1.0'))
        chrome = chrome_10.browser
        compat_body = """<tbody>
            <tr>
                <th>Feature</th><th>Chrome</th>
            </tr>
            <tr>
                <td>Basic support</td><td>1.0</td><td>{{CompatUnknown()}}</td>
            </tr>
            </tbody>"""
        expected = {
            'browsers': [{
                'id': chrome.id, 'name': 'Chrome', 'slug': 'chrome'}],
            'features': [{
                'id': '_basic support', 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'feature': '_basic support',
                'id': '__basic support-%s' % chrome_10.id,
                'support': 'yes', 'version': chrome_10.id}],
            'versions': [{
                'browser': chrome.id, 'id': chrome_10.id, 'version': '1.0'}]}
        self.assert_compat_body(
            compat_body, expected, [(158, 181, u'Extra cell in table')])

    def assert_compat_footnotes(self, compat_footnotes, expected, errors):
        parsed = page_grammar['compat_footnotes'].parse(compat_footnotes)
        footnotes = self.visitor.visit(parsed)
        self.assertEqual(expected, footnotes)
        self.assertEqual([], self.visitor.issues)
        self.assertEqual(errors, self.visitor.errors)

    def test_compat_footnotes_empty(self):
        footnotes = '\n'
        expected = {}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_simple(self):
        footnotes = "<p>[1] A footnote.</p>"
        expected = {'1': ('A footnote.', 0, 22)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_multi_paragraph(self):
        footnotes = "<p>[1] Footnote line 1.</p><p>Footnote line 2.</p>"
        expected = {
            '1': ("<p>Footnote line 1.</p>\n<p>Footnote line 2.</p>", 0, 50)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_multiple_footnotes(self):
        footnotes = "<p>[1] Footnote 1.</p><p>[2] Footnote 2.</p>"
        expected = {'1': ('Footnote 1.', 0, 22), '2': ('Footnote 2.', 22, 44)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_kumascript_cssxref(self):
        footnotes = '<p>[1] Use {{cssxref("-moz-border-image")}}</p>'
        expected = {'1': ('Use <code>-moz-border-image</code>', 0, 47)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_unknown_kumascriptscript(self):
        footnotes = (
            "<p>[1] Footnote {{UnknownKuma}} but the beat continues.</p>")
        expected = {'1': ('Footnote  but the beat continues.', 0, 59)}
        errors = [(15, 30, "Unknown footnote kumascript function UnknownKuma")]
        self.assert_compat_footnotes(footnotes, expected, errors)

    def test_compat_footnotes_unknown_kumascriptscript_with_args(self):
        footnotes = '<p>[1] Footnote {{UnknownKuma("arg")}}</p>'
        expected = {'1': ('Footnote ', 0, 42)}
        errors = [
            (15, 37,
             'Unknown footnote kumascript function UnknownKuma("arg")')]
        self.assert_compat_footnotes(footnotes, expected, errors)

    def test_compat_footnotes_pre_section(self):
        footnotes = '<p>[1] Here\'s some code:</p><pre>foo = bar</pre>'
        expected = {
            '1': ("<p>Here's some code:</p>\n<pre>foo = bar</pre>", 0, 48)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_pre_with_attrs_section(self):
        footnotes = (
            '<p>[1] Here\'s some code:</p>\n'
            '<pre class="brush:css">\n'
            '.foo {background-image: url(bg-image.png);}\n'
            '</pre>')
        expected = {
            '1': (
                "<p>Here's some code:</p>\n<pre class=\"brush:css\">\n"
                ".foo {background-image: url(bg-image.png);}\n</pre>",
                0, 103)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_asterisk(self):
        footnotes = "<p>[*] A footnote</p>"
        expected = {'1': ('A footnote', 0, 21)}
        self.assert_compat_footnotes(footnotes, expected, [])

    def test_compat_footnotes_bad_footnote(self):
        footnotes = "<p>A footnote.</p>"
        errors = [(0, 18, 'No ID in footnote.')]
        self.assert_compat_footnotes(footnotes, {}, errors)

    def assert_kumascript(self, text, name, args, errors=None):
        parsed = page_grammar['kumascript'].parse(text)
        expected = {
            'type': 'kumascript', 'name': name, 'args': args,
            'start': 0, 'end': len(text)}
        self.assertEqual(expected, self.visitor.visit(parsed))
        self.assertEqual(errors or [], self.visitor.errors)

    def test_kumascript_no_parens(self):
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
        self.assert_kumascript(
            ("{{SpecName('CSS3 Backgrounds', '#the-background-size',"
             " 'background-size')}}"),
            "SpecName",
            ["CSS3 Backgrounds", "#the-background-size",
             "background-size"])

    def assert_th(self, th, expected):
        parsed = page_grammar['th_elem'].parse(th)
        self.assertEqual(expected, self.visitor.visit(parsed))
        self.assertEqual([], self.visitor.issues)
        self.assertEqual([], self.visitor.errors)

    def test_th_elem_simple(self):
        th = '<th>Simple</th>'
        expected = {
            'type': 'th', 'start': 0, 'end': 4, 'attributes': {},
            'content': {'start': 4, 'end': 10, 'text': 'Simple'}}
        self.assert_th(th, expected)

    def test_th_elem_eat_whitespace(self):
        th = '<th> Eats Whitespace </th>'
        expected = {
            'type': 'th', 'start': 0, 'end': 4, 'attributes': {},
            'content': {'start': 5, 'end': 21, 'text': 'Eats Whitespace'}}
        self.assert_th(th, expected)

    def test_th_elem_attrs(self):
        th = '<th scope="col">Col Scope</th>'
        expected = {
            'type': 'th', 'start': 0, 'end': 16,
            'attributes': {'scope': {'start': 4, 'end': 15, 'value': 'col'}},
            'content': {'start': 16, 'end': 25, 'text': 'Col Scope'}}
        self.assert_th(th, expected)

    def test_th_elem_in_strong(self):
        th = '<th><strong>Strong</strong></th>'
        expected = {
            'type': 'th', 'start': 0, 'end': 4, 'attributes': {},
            'content': {
                'start': 12, 'end': 18, 'text': 'Strong', 'strong': True}}
        self.assert_th(th, expected)

    def test_cleanup_whitespace(self):
        text = """ This
        text <br/>
        has\t lots\xa0of
        extra&nbsp;whitespace.
        """
        expected = "This text has lots of extra whitespace."
        self.assertEqual(expected, self.visitor.cleanup_whitespace(text))

    def test_unquote_double(self):
        self.assertEqual('foo', self.visitor.unquote('"foo"'))

    def test_unquote_single(self):
        self.assertEqual('foo', self.visitor.unquote("'foo'"))

    def test_unquote_no_quote(self):
        self.assertEqual('27', self.visitor.unquote("27"))

    def test_unquote_unbalanced(self):
        self.assertRaises(ValueError, self.visitor.unquote, "'Mixed\"")

    def assert_browser_lookup(self, name, browser_id, fixed_name, slug):
        lookup = self.visitor.browser_id_name_and_slug(name)
        self.assertEqual(browser_id, lookup[0])
        self.assertEqual(fixed_name, lookup[1])
        self.assertEqual(slug, lookup[2])

    def test_browser_lookup_not_found(self):
        self.assert_browser_lookup(
            'Firefox (Gecko)', '_Firefox (Gecko)', 'Firefox',
            '_Firefox (Gecko)')

    def test_browser_id_name_and_slug_found(self):
        firefox = self.get_instance(Browser, 'firefox')
        self.assert_browser_lookup(
            'Firefox (Gecko)', firefox.id, 'Firefox', 'firefox')

    def test_browser_id_name_and_slug_cached(self):
        self.assert_browser_lookup(
            'Firefox (Gecko)', '_Firefox (Gecko)', 'Firefox',
            '_Firefox (Gecko)')
        self.get_instance(Browser, 'firefox')
        self.assert_browser_lookup(
            'Firefox (Gecko)', '_Firefox (Gecko)', 'Firefox',
            '_Firefox (Gecko)')  # Still not found

    def assert_feature_lookup(self, name, feature_id, slug):
        lookup = self.visitor.feature_id_and_slug(name)
        self.assertEqual(feature_id, lookup[0])
        self.assertEqual(slug, lookup[1])

    def test_feature_id_and_slug_not_found(self):
        self.assert_feature_lookup(
            'Basic support', '_basic support',
            'web-css-background-size_basic_support')

    def test_feature_id_and_slug_found(self):
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        self.assert_feature_lookup(
            'Basic support', feature.id,
            'web-css-background-size-basic_support')

    def test_feature_id_and_slug_cached(self):
        self.assert_feature_lookup(
            'Basic support', '_basic support',
            'web-css-background-size_basic_support')
        self.get_instance(Feature, 'web-css-background-size-basic_support')
        self.assert_feature_lookup(
            'Basic support', '_basic support',
            'web-css-background-size_basic_support')  # Still not found

    def test_feature_id_and_slug_existing_slug(self):
        self.create(Feature, slug='web-css-background-size_basic_support')
        self.assert_feature_lookup(
            'Basic support', '_basic support',
            'web-css-background-size_basic_support1')


class TestScrape(ScrapeTestCase):
    def setUp(self):
        self.feature = self.get_instance(Feature, 'web-css-background-size')

    def assertScrape(
            self, page, locale='en', specs=None, compat=None, footnotes=None,
            issues=None, errors=None):
        actual = scrape_page(page, self.feature)
        self.assertEqual(actual['locale'], locale)
        self.assertDataEqual(actual['specs'], specs or [])
        self.assertDataEqual(actual['compat'], compat or [])
        self.assertDataEqual(actual['footnotes'], footnotes)
        self.assertDataEqual(actual['issues'], issues or [])
        self.assertDataEqual(actual['errors'], errors or [])

    def test_empty(self):
        page = ""
        errors = ["No <h2> found in page"]
        self.assertScrape(page, errors=errors)

    def test_incomplete_parse_error(self):
        page = "<h2>Incomplete</h2><p>Incomplete</p>"
        errors = [
            (0, 36,
             'Unable to finish parsing MDN page, starting at this position.')]
        self.assertScrape(page, errors=errors)

    def test_spec_only(self):
        """Test with a only a Specification section."""
        page = self.sample_spec_section
        specs = [{
            'specification.mdn_key': 'CSS3 Backgrounds',
            'specification.id': None,
            'section.subpath': '#the-background-size',
            'section.name': 'background-size',
            'section.note': '',
            'section.id': None,
        }]
        errors = [(251, 335, 'Unknown Specification "CSS3 Backgrounds"')]
        self.assertScrape(page, specs=specs, errors=errors)


class FeaturePageTestCase(ScrapeTestCase):
    def setUp(self):
        path = "/en-US/docs/Web/CSS/background-size"
        url = "https://developer.mozilla.org" + path
        self.feature = self.get_instance(Feature, 'web-css-background-size')
        self.page = FeaturePage.objects.create(
            url=url, feature=self.feature, status=FeaturePage.STATUS_PARSING)
        meta = self.page.meta()
        meta.raw = dumps({
            'locale': 'en-US',
            'url': path,
            'translations': [{
                'locale': 'fr',
                'url': path.replace('en-US', 'fr')
            }]})
        meta.status = meta.STATUS_FETCHED
        meta.save()

    def empty_scrape(self):
        return {
            'locale': 'en', 'specs': [], 'issues': [], 'errors': [],
            'compat': [], 'footnotes': None}

    def empty_view(self, scraped_data):
        return {
            'features': {
                'experimental': False,
                'id': str(self.feature.id),
                'links': {
                    'children': [],
                    'parent': str(self.feature.parent.id),
                    'sections': [],
                    'supports': []},
                'mdn_uri': {
                    'en': ('https://developer.mozilla.org/en-US/docs/'
                           'Web/CSS/background-size'),
                    'fr': ('https://developer.mozilla.org/fr/docs/'
                           'Web/CSS/background-size')},
                'name': {'zxx': 'background-size'},
                'obsolete': False,
                'slug': 'web-css-background-size',
                'stable': True,
                'standardized': True,
            },
            'linked': {
                'browsers': [],
                'features': [],
                'maturities': [],
                'sections': [],
                'specifications': [],
                'supports': [],
                'versions': [],
            },
            'meta': {
                'compat_table': {
                    'languages': ['en', 'fr'],
                    'notes': {},
                    'pagination': {},
                    'supports': {str(self.feature.id): {}},
                    'tabs': []
                },
                'scrape': {
                    'errors': [],
                    'phase': 'Starting Import',
                    'raw': scraped_data}}}


class TestScrapedViewFeature(FeaturePageTestCase):
    def test_empty_scrape(self):
        scraped_data = self.empty_scrape()
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected = self.empty_view(scraped_data)
        self.assertDataEqual(expected, out)

    def test_load_specification(self):
        spec = self.get_instance(Specification, 'css3_backgrounds')
        maturity = spec.maturity
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        spec_content, mat_content = view.load_specification(spec.id)
        expected_spec = {
            'id': str(spec.id), 'slug': spec.slug, 'mdn_key': spec.mdn_key,
            'uri': spec.uri, 'name': spec.name,
            'links': {'maturity': str(maturity.id), 'sections': []}}
        self.assertDataEqual(expected_spec, spec_content)
        expected_mat = {
            'id': str(maturity.id), 'slug': maturity.slug,
            'name': maturity.name}
        self.assertDataEqual(expected_mat, mat_content)

    def test_new_specification(self):
        spec_row = {
            'section.note': 'section note',
            'section.subpath': '#section',
            'section.name': 'section',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': None}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        spec_content, mat_content = view.new_specification(spec_row)
        expected_spec = {
            'id': '_CSS3 UI', 'mdn_key': 'CSS3 UI',
            'links': {'maturity': '_unknown', 'sections': []}}
        self.assertDataEqual(expected_spec, spec_content)
        expected_mat = {
            'id': '_unknown', 'slug': '', 'name': {'en': 'Unknown'},
            'links': {'specifications': []}}
        self.assertDataEqual(expected_mat, mat_content)

    def test_load_section(self):
        section = self.get_instance(Section, 'background-size')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        section_content = view.load_section(section.id)
        expected = {
            'id': str(section.id),
            'name': section.name, 'note': {},
            'number': None, 'subpath': section.subpath,
            'links': {'specification': str(section.specification.id)}}
        self.assertDataEqual(expected, section_content)

    def test_new_section(self):
        spec_row = {
            'section.note': 'section note',
            'section.subpath': '#section',
            'section.name': 'section',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': None}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        section_content = view.new_section(spec_row, '_CSS3_UI')
        expected = {
            'id': '_CSS3_UI_#section',
            'name': {'en': 'section'}, 'note': {'en': 'section note'},
            'number': None, 'subpath': {'en': '#section'},
            'links': {'specification': '_CSS3_UI'}}
        self.assertDataEqual(expected, section_content)

    def test_load_browser(self):
        browser = self.get_instance(Browser, 'firefox')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        browser_content = view.load_browser(browser.id)
        expected = {
            'id': str(browser.id), 'name': {'en': 'Firefox'}, 'note': None,
            'slug': browser.slug}
        self.assertDataEqual(expected, browser_content)

    def test_new_browser(self):
        browser_entry = {
            'id': '_Firefox (Gecko)', 'name': 'Firefox',
            'slug': '_Firefox (Gecko)'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        browser_content = view.new_browser(browser_entry)
        expected = {
            'id': '_Firefox (Gecko)', 'name': {'en': 'Firefox'}, 'note': None,
            'slug': ''}
        self.assertDataEqual(expected, browser_content)

    def test_load_version(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        version_content = view.load_version(version.id)
        expected = {
            'id': str(version.id), 'version': '1.0', 'status': 'unknown',
            'note': None, 'release_day': None, 'retirement_day': None,
            'release_notes_uri': None, 'order': 0,
            'links': {'browser': str(version.browser_id)}}
        self.assertDataEqual(expected, version_content)

    def test_new_version(self):
        version_entry = {
            'id': '_version', 'browser': '_browser', 'version': '1.0'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        version_content = view.new_version(version_entry)
        expected = {
            'id': '_version', 'version': '1.0', 'status': 'unknown',
            'note': None, 'release_day': None, 'retirement_day': None,
            'release_notes_uri': None,
            'links': {'browser': '_browser'}}
        self.assertDataEqual(expected, version_content)

    def test_load_feature(self):
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.load_feature(feature.id)
        expected = {
            'id': str(feature.id), 'name': {'en': 'Basic support'},
            'slug': feature.slug, 'mdn_uri': None, 'obsolete': False,
            'stable': True, 'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'sections': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_new_feature(self):
        feature_entry = {
            'id': '_feature', 'name': 'Basic support',
            'slug': 'web-css-background-size_basic_support'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.new_feature(feature_entry)
        expected = {
            'id': '_feature', 'name': {'en': 'Basic support'},
            'slug': 'web-css-background-size_basic_support',
            'mdn_uri': None, 'obsolete': False, 'stable': True,
            'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'sections': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_new_feature_canonical(self):
        feature_entry = {
            'id': '_feature', 'name': 'cover', 'canonical': True,
            'slug': 'web-css-background-size_cover'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.new_feature(feature_entry)
        expected = {
            'id': '_feature', 'name': 'cover',
            'slug': 'web-css-background-size_cover',
            'mdn_uri': None, 'obsolete': False, 'stable': True,
            'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'sections': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_load_support(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        support = self.create(Support, version=version, feature=feature)
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        support_content = view.load_support(support.id)
        expected = {
            'id': str(support.id), 'support': 'yes', 'note': None,
            'prefix': None, 'prefix_mandatory': False, 'protected': False,
            'requires_config': None, 'default_config': None,
            'alternate_name': None, 'alternate_mandatory': False,
            'links': {'feature': str(feature.id), 'version': str(version.id)}}
        self.assertDataEqual(expected, support_content)

    def test_new_support(self):
        support_entry = {
            'id': '_support', 'feature': '_feature', 'version': '_version',
            'support': 'yes'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        support_content = view.new_support(support_entry)
        expected = {
            'id': '_support', 'support': 'yes', 'note': None,
            'prefix': None, 'prefix_mandatory': False, 'protected': False,
            'requires_config': None, 'default_config': None,
            'alternate_name': None, 'alternate_mandatory': False,
            'links': {'feature': '_feature', 'version': '_version'}}
        self.assertDataEqual(expected, support_content)

    def test_new_support_with_note(self):
        support_entry = {
            'id': '_support', 'feature': '_feature', 'version': '_version',
            'support': 'yes', 'footnote': 'The Footnote'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        support_content = view.new_support(support_entry)
        expected = {
            'id': '_support', 'support': 'yes', 'note': {'en': 'The Footnote'},
            'prefix': None, 'prefix_mandatory': False, 'protected': False,
            'requires_config': None, 'default_config': None,
            'alternate_name': None, 'alternate_mandatory': False,
            'links': {'feature': '_feature', 'version': '_version'}}
        self.assertDataEqual(expected, support_content)

    def test_load_specification_row_new_resources(self):
        scraped_data = self.empty_scrape()
        scraped_spec = {
            'section.note': 'section note',
            'section.subpath': '#section',
            'section.name': 'section',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': None}
        scraped_data['specs'].append(scraped_spec)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        spec_content, mat_content = view.new_specification(scraped_spec)
        section_content = view.new_section(scraped_spec, spec_content['id'])
        expected = self.empty_view(scraped_data)
        expected['features']['links']['sections'] = [section_content['id']]
        expected['linked']['maturities'] = [mat_content]
        expected['linked']['specifications'] = [spec_content]
        expected['linked']['sections'] = [section_content]
        self.assertDataEqual(expected, out)

    def test_load_specification_row_existing_resources(self):
        section = self.get_instance(Section, 'background-size')
        spec = section.specification
        scraped_spec = {
            'section.note': 'new note',
            'section.subpath': section.subpath['en'],
            'section.name': section.name['en'],
            'specification.mdn_key': spec.mdn_key,
            'section.id': section.id,
            'specification.id': spec.id}
        scraped_data = self.empty_scrape()
        scraped_data['specs'].append(scraped_spec)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected = self.empty_view(scraped_data)
        spec_content, mat_content = view.load_specification(spec.id)
        section_content = view.load_section(section.id)
        section_content['note'] = {'en': 'new note'}
        expected['features']['links']['sections'] = [str(section.id)]
        expected['linked']['maturities'] = [mat_content]
        expected['linked']['specifications'] = [spec_content]
        expected['linked']['sections'] = [section_content]
        self.assertDataEqual(expected, out)

    def test_load_compat_table_new_resources(self):
        browser_id = '_Firefox (Gecko)'
        version_id = '_Firefox-1.0'
        feature_id = '_basic_support'
        support_id = '_%s-%s' % (feature_id, version_id)
        scraped_data = self.empty_scrape()
        scraped_table = {
            'name': 'desktop',
            'browsers': [{
                'id': browser_id, 'name': 'Firefox',
                'slug': '_Firefox (Gecko)'}],
            'versions': [{
                'id': version_id, 'browser': browser_id, 'version': '1.0'}],
            'features': [{
                'id': feature_id, 'name': 'Basic support',
                'slug': 'web-css-background-size_basic_support'}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        browser_content = view.new_browser(scraped_table['browsers'][0])
        version_content = view.new_version(scraped_table['versions'][0])
        feature_content = view.new_feature(scraped_table['features'][0])
        support_content = view.new_support(scraped_table['supports'][0])
        expected = self.empty_view(scraped_data)
        expected['linked']['browsers'].append(browser_content)
        expected['linked']['versions'].append(version_content)
        expected['linked']['features'].append(feature_content)
        expected['linked']['supports'].append(support_content)
        expected['meta']['compat_table']['supports'][feature_id] = {
            browser_id: [support_id]}
        expected['meta']['compat_table']['tabs'].append({
            'name': {'en': 'Desktop Browsers'}, 'browsers': [browser_id]})
        self.assertDataEqual(expected, out)

    def test_load_compat_table_existing_resources(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        support = self.create(Support, version=version, feature=feature)
        browser_id = str(browser.id)
        version_id = str(version.id)
        feature_id = str(feature.id)
        support_id = str(support.id)
        scraped_data = self.empty_scrape()
        scraped_table = {
            'name': 'desktop',
            'browsers': [{
                'id': browser_id, 'name': browser.name['en'],
                'slug': browser.slug}],
            'versions': [{
                'id': version_id, 'browser': browser_id, 'version': '1.0'}],
            'features': [{
                'id': feature_id, 'name': feature.name['en'],
                'slug': feature.slug}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected = self.empty_view(scraped_data)
        expected['linked']['browsers'].append(view.load_browser(browser.id))
        expected['linked']['versions'].append(view.load_version(version.id))
        expected['linked']['features'].append(view.load_feature(feature.id))
        expected['linked']['supports'].append(view.load_support(support.id))
        expected['meta']['compat_table']['supports'][feature_id] = {
            browser_id: [support_id]}
        expected['meta']['compat_table']['tabs'].append({
            'name': {'en': 'Desktop Browsers'},
            'browsers': [browser_id]})
        self.assertDataEqual(expected, out)

    def test_load_compat_table_new_support_with_note(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        browser_id = str(browser.id)
        version_id = str(version.id)
        feature_id = str(feature.id)
        support_id = '_%s-%s' % (feature_id, version_id)
        scraped_data = self.empty_scrape()
        scraped_table = {
            'name': 'desktop',
            'browsers': [{
                'id': browser_id, 'name': browser.name['en'],
                'slug': browser.slug}],
            'versions': [{
                'id': version_id, 'browser': browser_id, 'version': '1.0'}],
            'features': [{
                'id': feature_id, 'name': feature.name['en'],
                'slug': feature.slug}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes', 'footnote': 'Footnote'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected = self.empty_view(scraped_data)
        support_content = view.new_support(scraped_table['supports'][0])
        expected['linked']['browsers'].append(view.load_browser(browser.id))
        expected['linked']['versions'].append(view.load_version(version.id))
        expected['linked']['features'].append(view.load_feature(feature.id))
        expected['linked']['supports'].append(support_content)
        expected['meta']['compat_table']['supports'][feature_id] = {
            browser_id: [support_id]}
        expected['meta']['compat_table']['tabs'].append({
            'name': {'en': 'Desktop Browsers'},
            'browsers': [browser_id]})
        expected['meta']['compat_table']['notes'][support_id] = 1
        self.assertDataEqual(expected, out)


class TestScrapeFeaturePage(FeaturePageTestCase):
    def set_content(self, content):
        for translation in self.page.translations():
            translation.status = translation.STATUS_FETCHED
            translation.raw = content
            translation.save()

    def test_empty_page(self):
        self.set_content('')
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED, fp.status)
        expected_error = ['<pre>No &lt;h2&gt; found in page</pre>']
        self.assertEqual(expected_error, fp.data['meta']['scrape']['errors'])
        self.assertTrue(fp.has_issues)

    def test_parse_issue(self):
        bad_page = '''\
<p>The page has a bad specification section.</p>
<h2 id="Specifications">Specifications</h2>
<p>No specs</p>
'''
        self.set_content(bad_page)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED, fp.status)
        expected_error = [range_error_to_html(
            bad_page, 93, 108,
            'Section <h2>Specifications</h2> was not parsed. The parser'
            ' failed on rule "spec_table", but the real cause may be'
            ' unexpected content after this position. Definition:',
            'spec_table = "<table class="standard-table">" _ spec_head'
            ' _ spec_body _ "</table>" _')]
        self.assertEqual(expected_error, fp.data['meta']['scrape']['errors'])
        self.assertTrue(fp.has_issues)


class TestRangeErrorToHtml(ScrapeTestCase):
    def test_no_rule(self):
        html = range_error_to_html(
            self.sample_page, 902, 986,
            'Unknown Specification "CSS3 Backgrounds"')
        expected = """\
<div><p>Unknown Specification &quot;CSS3 Backgrounds&quot;</p><p>Context:\
<pre>32      &lt;td&gt;{{CompatGeckoDesktop(&quot;1&quot;)}}&lt;/td&gt;
33    &lt;/tr&gt;
34   &lt;/tbody&gt;
**        ^^^
35  &lt;/table&gt;
** ^^^^^^^^^
36 &lt;/div&gt;
** ^^^^^^
37 &lt;h2 id=&quot;See_also&quot;&gt;See also&lt;/h2&gt;
** ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
38 &lt;ul&gt;
** ^^^^
39  &lt;li&gt;{{CSS_Reference:Position}}&lt;/li&gt;
** ^^^^^^^^^^^^^^^^^^^^^^^^^^          \n\
</pre></p></div>"""
        self.assertEqual(expected, html)

    def test_rule(self):
        html = range_error_to_html(
            self.sample_page, 902, 986,
            'Unknown Specification "CSS3 Backgrounds"',
            'me = "awesome"')
        expected = """\
<div><p>Unknown Specification &quot;CSS3 Backgrounds&quot;</p>\
<p><code>me = &quot;awesome&quot;</code></p>\
<p>Context:<pre>32      &lt;td&gt;{{CompatGeckoDesktop(&quot;1&quot;)}}\
&lt;/td&gt;
33    &lt;/tr&gt;
34   &lt;/tbody&gt;
**        ^^^
35  &lt;/table&gt;
** ^^^^^^^^^
36 &lt;/div&gt;
** ^^^^^^
37 &lt;h2 id=&quot;See_also&quot;&gt;See also&lt;/h2&gt;
** ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
38 &lt;ul&gt;
** ^^^^
39  &lt;li&gt;{{CSS_Reference:Position}}&lt;/li&gt;
** ^^^^^^^^^^^^^^^^^^^^^^^^^^          \n\
</pre></p></div>"""
        self.assertEqual(expected, html)


class TestSlugify(TestCase):
    def test_already_slugged(self):
        self.assertEqual('foo', slugify('foo'))

    def test_long_string(self):
        self.assertEqual(
            'abcdefghijklmnopqrstuvwxyz-abcdefghijklmnopqrstuvw',
            slugify('ABCDEFGHIJKLMNOPQRSTUVWXYZ-abcdefghijklmnopqrstuvwxyz'))

    def test_non_ascii(self):
        self.assertEqual('_', slugify("Рекомендация"))

    def test_limit(self):
        self.assertEqual(
            'abcdefghij', slugify('ABCDEFGHIJKLMNOPQRSTUVWXYZ', length=10))

    def test_num_suffix(self):
        self.assertEqual('slug13', slugify('slug', suffix=13))


class TestDateToIso(TestCase):
    def test_date(self):
        self.assertEqual('2015-02-02', date_to_iso(date(2015, 2, 2)))

    def test_none(self):
        self.assertEqual(None, date_to_iso(''))
