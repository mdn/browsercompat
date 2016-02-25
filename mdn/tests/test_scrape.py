# coding: utf-8
"""Test mdn.scrape."""
from __future__ import unicode_literals
from json import dumps

from mdn.models import FeaturePage
from mdn.scrape import (
    narrow_parse_error, scrape_page, scrape_feature_page, PageExtractor,
    PageVisitor, ScrapedViewFeature)
from mdn.kumascript import kumascript_grammar
from webplatformcompat.models import Feature, Support
from .base import TestCase


class BaseTestCase(TestCase):
    def setUp(self):
        self.feature = self.get_instance('Feature', 'web-css-background-size')

    def get_sample_specs(self):
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
   <tr>
     <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',\
 'background-size')}}</td>
     <td>{{Spec2('CSS3 Backgrounds')}}</td>
     <td></td>
   </tr>
 </tbody>
</table>
"""
        spec = self.get_instance('Specification', 'css3_backgrounds')
        expected_specs = [{
            'specification.id': spec.id,
            'specification.mdn_key': 'CSS3 Backgrounds',
            'section.id': None, 'section.name': 'background-size',
            'section.note': '', 'section.subpath': '#the-background-size'}]
        return sample_spec_section, expected_specs

    def get_sample_compat(self):
        sample_compat_section = """\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{CompatibilityTable}}</div>
<div id="compat-desktop">
 <table class="compat-table">
  <tbody>
   <tr><th>Feature</th><th>Firefox (Gecko)</th></tr>
   <tr>
    <td><code>contain</code> and <code>cover</code></td>
    <td>{{CompatGeckoDesktop("1")}}</td>
   </tr>
  </tbody>
 </table>
</div>
"""
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        browser_id = version.browser_id
        version_id = version.id
        expected_compat = [{
            'name': u'desktop',
            'browsers': [{
                'id': browser_id, 'name': 'Firefox for Desktop',
                'slug': 'firefox_desktop'}],
            'versions': [{
                'browser': browser_id, 'id': version_id, 'version': '1.0'}],
            'features': [{
                'id': '_contain and cover',
                'name': '<code>contain</code> and <code>cover</code>',
                'slug': 'web-css-background-size_contain_and_cover'}],
            'supports': [{
                'feature': '_contain and cover',
                'id': '__contain and cover-%s' % version_id,
                'support': 'yes', 'version': version_id}]}]
        return sample_compat_section, expected_compat


class TestPageExtractor(BaseTestCase):
    def setUp(self):
        super(TestPageExtractor, self).setUp()
        self.visitor = PageVisitor()

    def assert_extract(
            self, page, specs=None, compat=None, footnotes=None, issues=None):
        parsed = kumascript_grammar.parse(page)
        elements = self.visitor.visit(parsed)
        extractor = PageExtractor(elements=elements, feature=self.feature)
        extracted = extractor.extract()
        self.assertEqual(specs or [], extracted['specs'])
        self.assertEqual(compat or [], extracted['compat'])
        self.assertEqual(footnotes, extracted['footnotes'])
        self.assertEqual(issues or [], extracted['issues'])

    def test_valid_spec_section(self):
        sample_spec_section, expected_specs = self.get_sample_specs()
        self.assert_extract(sample_spec_section, specs=expected_specs)

    def test_invalid_spec_section(self):
        page = '<h2>Specifications</h2><p>Incomplete</p>'
        self.assert_extract(page, issues=[('skipped_content', 23, 40, {})])

    def test_valid_compat_section(self):
        sample_compat_section, expected_compat = self.get_sample_compat()
        self.assert_extract(sample_compat_section, compat=expected_compat)

    def test_invalid_compat_section(self):
        page = '<h2>Browser Compatibility</h2><p>Not present</p>'
        self.assert_extract(page, issues=[('skipped_content', 30, 48, {})])

    def test_full_page(self):
        sample_spec_section, expected_specs = self.get_sample_specs()
        sample_compat_section, expected_compat = self.get_sample_compat()
        page = """\
<p>Some lead content</p>
<h2>Other Text</h2>
<p>Here's some other content</p>
%s
%s
<h2>Other Pages</h2>
<p>See <a href="/foo">foo</a></p>
""" % (sample_spec_section, sample_compat_section)
        self.assert_extract(page, specs=expected_specs, compat=expected_compat)

    def test_full_page_reversed_sections(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1175177
        # https://developer.mozilla.org/en-US/docs/Web/API/Blob/slice
        sample_spec_section, expected_specs = self.get_sample_specs()
        sample_compat_section, expected_compat = self.get_sample_compat()
        page = """\
<p>Some lead content</p>
<h2>Other Text</h2>
<p>Here's some other content</p>
<h3>More Detail</h3>
<p>Trigger &lt;h3&gt; check not in a compat section.</p>
%s
%s
<h2>Other Pages</h2>
<p>See <a href="/foo">foo</a></p>
""" % (sample_compat_section, sample_spec_section)
        self.assert_extract(page, specs=expected_specs, compat=expected_compat)

    def test_compat_h3(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MozContact/key
        sample_compat_section, expected_compat = self.get_sample_compat()
        page = (
            sample_compat_section +
            '<h3 id="Gecko Gecko">Gecko Note</h3>\n<p>A note</p>')
        issues = [('skipped_h3', 354, 390, {'h3': 'Gecko Note'})]
        self.assert_extract(page, compat=expected_compat, issues=issues)

    def test_div_wrapped(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Document/execCommand
        sample_spec_section, expected_specs = self.get_sample_specs()
        sample_compat_section, expected_compat = self.get_sample_compat()
        page = """\
<p>Some lead content</p>
<div>
%s
%s
</div>
""" % (sample_spec_section, sample_compat_section)
        issue = ('no_data', 0, 24, {})
        self.assert_extract(page, issues=[issue])


class TestScrape(BaseTestCase):
    def assertScrape(self, page, specs, issues):
        actual = scrape_page(page, self.feature)
        self.assertEqual(actual['locale'], 'en')
        self.assertDataEqual(actual['specs'], specs)
        self.assertDataEqual(actual['compat'], [])
        self.assertDataEqual(actual['footnotes'], None)
        self.assertDataEqual(actual['issues'], issues)
        self.assertDataEqual(actual['embedded_compat'], None)

    def test_empty(self):
        page = ''
        self.assertScrape(page, [], [])

    def test_not_compat_page(self):
        page = "<h3>I'm not a compat page</h3>"
        self.assertScrape(page, [], [])

    def test_incomplete_parse_error(self):
        page = """
<html>
  <head>
    <title>Fragment expected</title>
  </head>
  <body>
  <h1>Page</h1>
  <h2>Specifications</h2>
  <p>The parser expects a page fragment, not a full document.</p>
  </body>
</html>"""
        self.assertScrape(page, [], [('halt_import', 21, 53, {})])

    def test_spec_only(self):
        """Test with a only a Specification section."""
        sample_spec_section, expected_specs = self.get_sample_specs()
        self.assertScrape(sample_spec_section, expected_specs, [])


class TestNarrowParseError(TestCase):
    def test_unknown_element(self):
        html = """\
<ul>
  <li>Plain</li>
  <li><strong>Bold</strong></li>
  <li><unknown>Strange</unknown></li>
  <li><em>Emphasized</em></li>
</ul>"""
        narrow_pos, narrow_end = narrow_parse_error(html, 0)
        expected_pos = html.index('<unknown>')
        expected_end = html.index('</li>', expected_pos)
        self.assertEqual(expected_pos, narrow_pos)
        self.assertEqual(expected_end, narrow_end)

    def test_unknown_with_attributes(self):
        html = '<p><unknown class="foo">foo</unknown></p>'
        narrow_pos, narrow_end = narrow_parse_error(html, 3)
        expected_pos = html.index('<unknown')
        expected_end = html.index('</p>', expected_pos)
        self.assertEqual(expected_pos, narrow_pos)
        self.assertEqual(expected_end, narrow_end)

    def test_no_end_tag(self):
        html = '<p>This is <strong>bold</p></strong>'
        narrow_pos, narrow_end = narrow_parse_error(html, 0)
        expected_pos = html.index('<strong')
        expected_end = html.index('</p>', expected_pos)
        self.assertEqual(expected_pos, narrow_pos)
        self.assertEqual(expected_end, narrow_end)

    def test_inner_lt(self):
        html = '<p><div>4 < 5</div></p>'
        narrow_pos, narrow_end = narrow_parse_error(html, 0)
        self.assertEqual(html.index('<div>'), narrow_pos)
        self.assertEqual(html.index('</p>'), narrow_end)

    def test_naked_lt(self):
        html = "Here's a naked < Wow that might cause problems."
        pos = html.index('<')
        narrow_pos, narrow_end = narrow_parse_error(html, pos)
        self.assertEqual(pos, narrow_pos)
        self.assertEqual(len(html), narrow_end)

    def test_non_element_error(self):
        html = '<p>unknown [error]</p>'
        narrow_pos, narrow_end = narrow_parse_error(html, 10)
        self.assertEqual(10, narrow_pos)
        self.assertEqual(len(html), narrow_end)


class FeaturePageTestCase(TestCase):
    def setUp(self):
        path = '/en-US/docs/Web/CSS/background-size'
        url = 'https://developer.mozilla.org' + path
        self.feature = self.get_instance('Feature', 'web-css-background-size')
        self.page = FeaturePage.objects.create(
            url=url, feature=self.feature, status=FeaturePage.STATUS_PARSING)
        meta = self.page.meta()
        meta.raw = dumps({
            'locale': 'en-US', 'url': path, 'title': 'background-size',
            'translations': [{
                'locale': 'fr',
                'url': path.replace('en-US', 'fr'),
                'title': 'background-size',
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
                    'references': [],
                    'supports': []},
                'mdn_uri': {
                    'en': ('https://developer.mozilla.org/en-US/docs/'
                           'Web/CSS/background-size'),
                    'fr': ('https://developer.mozilla.org/fr/docs/'
                           'Web/CSS/background-size')},
                'name': 'background-size',
                'obsolete': False,
                'slug': 'web-css-background-size',
                'stable': True,
                'standardized': True,
            },
            'linked': {
                'browsers': [],
                'features': [],
                'maturities': [],
                'references': [],
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
                    'phase': 'Starting Import',
                    'issues': [],
                    'embedded_compat': None,
                }}}


class TestScrapedViewFeature(FeaturePageTestCase):
    def test_empty_scrape(self):
        scraped_data = self.empty_scrape()
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected = self.empty_view(scraped_data)
        self.assertDataEqual(expected, out)

    def test_load_specification(self):
        spec = self.get_instance('Specification', 'css3_backgrounds')
        maturity = spec.maturity
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        spec_content, mat_content = view.load_specification(spec.id)
        expected_spec = {
            'id': str(spec.id), 'slug': spec.slug, 'mdn_key': spec.mdn_key,
            'uri': spec.uri, 'name': spec.name,
            'links': {'maturity': str(maturity.id)}}
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
            'links': {'maturity': '_unknown'}}
        self.assertDataEqual(expected_spec, spec_content)
        expected_mat = {
            'id': '_unknown', 'slug': '', 'name': {'en': 'Unknown'},
            'links': {'specifications': []}}
        self.assertDataEqual(expected_mat, mat_content)

    def test_load_section(self):
        section = self.get_instance('Section', 'background-size')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        section_content = view.load_section(section.id)
        expected = {
            'id': str(section.id), 'name': section.name,
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
            'id': '__CSS3_UI_#section', 'name': {'en': 'section'},
            'number': None, 'subpath': {'en': '#section'},
            'links': {'specification': '_CSS3_UI'}}
        self.assertDataEqual(expected, section_content)

    def test_load_browser(self):
        browser = self.get_instance('Browser', 'firefox_desktop')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        browser_content = view.load_browser(browser.id)
        expected = {
            'id': str(browser.id), 'name': {'en': 'Firefox for Desktop'},
            'note': None, 'slug': browser.slug}
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
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
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

    def test_new_unnamed_current_version(self):
        version_entry = {
            'id': '_version', 'browser': '_browser', 'version': ''}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        version_content = view.new_version(version_entry)
        expected = {
            'id': '_version', 'version': 'current', 'status': 'current',
            'note': None, 'release_day': None, 'retirement_day': None,
            'release_notes_uri': None,
            'links': {'browser': '_browser'}}
        self.assertDataEqual(expected, version_content)

    def test_new_nightly_version(self):
        version_entry = {
            'id': '_version', 'browser': '_browser', 'version': 'nightly'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        version_content = view.new_version(version_entry)
        expected = {
            'id': '_version', 'version': 'nightly', 'status': 'future',
            'note': None, 'release_day': None, 'retirement_day': None,
            'release_notes_uri': None,
            'links': {'browser': '_browser'}}
        self.assertDataEqual(expected, version_content)

    def test_load_feature(self):
        feature = self.get_instance(
            'Feature', 'web-css-background-size-contain_and_cover')
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.load_feature(feature.id)
        expected = {
            'id': str(feature.id),
            'name': {'en': '<code>contain</code> and <code>cover</code>'},
            'slug': feature.slug, 'mdn_uri': None, 'obsolete': False,
            'stable': True, 'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'references': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_load_feature_canonical_name(self):
        feature = self.create(
            Feature, slug='web-css-background-size_list-item',
            name={'zxx': 'list-item'}, parent=self.feature)
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.load_feature(feature.id)
        expected = {
            'id': str(feature.id), 'name': 'list-item',
            'slug': feature.slug, 'mdn_uri': None, 'obsolete': False,
            'stable': True, 'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'references': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_new_feature(self):
        feature_entry = {
            'id': '_feature',
            'name': '<code>contain</code> and <code>cover</code>',
            'slug': 'web-css-background-size_contain_and_cover'}
        view = ScrapedViewFeature(self.page, self.empty_scrape())
        feature_content = view.new_feature(feature_entry)
        expected = {
            'id': '_feature',
            'name': {'en': '<code>contain</code> and <code>cover</code>'},
            'slug': 'web-css-background-size_contain_and_cover',
            'mdn_uri': None, 'obsolete': False, 'stable': True,
            'standardized': True, 'experimental': False,
            'links': {
                'children': [], 'parent': str(self.feature.id),
                'references': [], 'supports': []}}
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
                'references': [], 'supports': []}}
        self.assertDataEqual(expected, feature_content)

    def test_load_support(self):
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        feature = self.get_instance(
            'Feature', 'web-css-background-size-contain_and_cover')
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
        section_content['name']['en'] = 'section'
        section_content['subpath']['en'] = '#section'
        reference_content = view.load_or_new_reference(section_content['id'])
        reference_content['note']['en'] = 'section note'
        expected = self.empty_view(scraped_data)
        expected['features']['links']['references'] = [reference_content['id']]
        expected['linked']['maturities'] = [mat_content]
        expected['linked']['specifications'] = [spec_content]
        expected['linked']['sections'] = [section_content]
        expected['linked']['references'] = [reference_content]
        self.assertDataEqual(expected, out)

    def test_load_specification_row_empty_resources(self):
        scraped_data = self.empty_scrape()
        scraped_spec = {
            'section.note': '',
            'section.subpath': '',
            'section.name': '',
            'specification.mdn_key': 'CSS3 UI',
            'section.id': None,
            'specification.id': None}
        scraped_data['specs'].append(scraped_spec)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        spec_content, mat_content = view.new_specification(scraped_spec)
        section_content = view.new_section(scraped_spec, spec_content['id'])
        # TODO: bug 1251252 - Empty string should mean omittied name, subpath
        section_content['name']['en'] = ''
        section_content['subpath']['en'] = ''
        reference_content = view.load_or_new_reference(section_content['id'])
        reference_content['note'] = None
        expected = self.empty_view(scraped_data)
        expected['features']['links']['references'] = [reference_content['id']]
        expected['linked']['maturities'] = [mat_content]
        expected['linked']['specifications'] = [spec_content]
        expected['linked']['sections'] = [section_content]
        expected['linked']['references'] = [reference_content]
        self.assertDataEqual(expected, out)

    def test_load_specification_row_existing_resources(self):
        reference = self.get_instance(
            'Reference', ('web-css-background-size', 'background-size'))
        section = reference.section
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
        reference_content = view.load_or_new_reference(section.id)
        reference_content['note'] = {'en': 'new note'}
        expected['features']['links']['references'] = [reference_content['id']]
        expected['linked']['maturities'] = [mat_content]
        expected['linked']['specifications'] = [spec_content]
        expected['linked']['sections'] = [section_content]
        expected['linked']['references'] = [reference_content]
        self.assertDataEqual(expected, out)

    def test_load_compat_table_new_resources(self):
        browser_id = '_Firefox (Gecko)'
        version_id = '_Firefox-1.0'
        feature_id = '_contain_and_cover'
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
                'id': feature_id,
                'name': '<code>contain</code> and <code>cover</code>',
                'slug': 'web-css-background-size_contain_and_cover'}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        browser_content = view.new_browser(scraped_table['browsers'][0])
        version_content = view.new_version(scraped_table['versions'][0])
        feature_content = view.new_feature(scraped_table['features'][0])
        feature_content['links']['supports'].append(support_id)
        support_content = view.new_support(scraped_table['supports'][0])
        expected = self.empty_view(scraped_data)
        expected['features']['links']['children'] = [feature_id]
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
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            'Feature', 'web-css-background-size-contain_and_cover')
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
        expected['features']['links']['children'] = [feature_id]
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

    def test_load_compat_table_basic_support(self):
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        browser = version.browser
        feature = self.feature
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
                'id': feature_id, 'name': 'Basic Support',
                'slug': feature.slug}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        expected_tabs = [
            {'name': {'en': 'Desktop Browsers'}, 'browsers': [browser_id]}]
        self.assertEqual(expected_tabs, out['meta']['compat_table']['tabs'])

    def test_load_compat_table_new_support_with_note(self):
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        browser = version.browser
        feature = self.get_instance(
            'Feature', 'web-css-background-size-contain_and_cover')
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
        self.assertEqual(1, out['meta']['compat_table']['notes'][support_id])

    def test_load_compat_table_unicode_feature_name(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/timing-function
        browser_id = '_Firefox (Gecko)'
        version_id = '_Firefox-1.0'
        feature_id = '_cubic-bezier() w/ ordinate ∉[0,1]'
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
                'id': feature_id,
                'name': '<code>cubic-bezier()</code> w/ ordinate ∉[0,1]',
                'slug': 'web-css-background-size_unicode'}],
            'supports': [{
                'id': support_id, 'feature': feature_id, 'version': version_id,
                'support': 'yes'}]}
        scraped_data['compat'].append(scraped_table)
        view = ScrapedViewFeature(self.page, scraped_data)
        out = view.generate_data()
        self.assertEqual(feature_id, out['linked']['features'][0]['id'])


class TestScrapeFeaturePage(FeaturePageTestCase):

    # MDN raw content with minimal specification data
    good_content = '''\
<h2 id="Specifications">Specifications</h2>
<table class="standard-table">
 <thead>
  <tr>
   <th scope="col">Specification</th>
   <th scope="col">Status</th>
   <th scope="col">Comment</th>
  </tr>
 </thead>
 <tbody>
   <tr>
     <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',\
 'background-size')}}</td>
     <td>{{Spec2('CSS3 Backgrounds')}}</td>
     <td></td>
   </tr>
 </tbody>
</table>
'''

    def set_content(self, content):
        found = False
        for data in self.page.translations():
            translation = data.obj
            if data.obj is None:
                continue
            found = True
            translation.status = translation.STATUS_FETCHED
            translation.raw = content
            translation.save()
        assert found, 'No English translation object found in translations'

    def test_empty_page(self):
        self.set_content('  ')
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_NO_DATA, fp.status)
        self.assertEqual([], fp.data['meta']['scrape']['issues'])
        self.assertFalse(fp.has_issues)
        self.assertEqual(fp.CONVERTED_NO_DATA, fp.converted_compat)
        self.assertEqual(fp.COMMITTED_NO_DATA, fp.committed)

    def test_parse_warning(self):
        bad_content = '''\
<p>The page has a bad specification section.</p>
<h2 id="Specifications">Specifications</h2>
<p>No specs</p>
'''
        self.set_content(bad_content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED_WARNING, fp.status)
        self.assertEqual(
            [['skipped_content', 93, 108, {}, 'en-US']],
            fp.data['meta']['scrape']['issues'])
        self.assertTrue(fp.has_issues)
        self.assertEqual(fp.COMMITTED_NO_DATA, fp.committed)

    def test_parse_error(self):
        self.get_instance('Specification', 'css3_backgrounds')
        bad_content = self.good_content.replace('Spec2', 'SpecName')
        self.set_content(bad_content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED_ERROR, fp.status)
        self.assertTrue(fp.has_issues)
        self.assertEqual(fp.COMMITTED_NEEDS_FIXES, fp.committed)

    def test_parse_critical(self):
        # A page with a div element wrapping the content
        bad_content = '''\
<div>
  <h2 id="Specifications">Specifications</h2>
  <p>No specs</p>
</div>
'''
        self.set_content(bad_content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED_CRITICAL, fp.status)
        self.assertTrue(fp.has_issues)

    def test_parse_ok(self):
        self.get_instance('Specification', 'css3_backgrounds')
        self.set_content(self.good_content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED, fp.status)
        self.assertFalse(fp.has_issues)
        self.assertEqual(fp.CONVERTED_NO, fp.converted_compat)
        self.assertEqual(fp.COMMITTED_NO, fp.committed)

    def test_parse_embedcompattable(self):
        self.get_instance('Specification', 'css3_backgrounds')
        content = self.good_content + '''\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{EmbedCompatTable("web-css-background-size")}}</div>
'''
        self.set_content(content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED, fp.status, fp.get_status_display())
        self.assertFalse(fp.has_issues)
        self.assertEqual(fp.CONVERTED_YES, fp.converted_compat)
        self.assertEqual(fp.COMMITTED_NO, fp.committed)

    def test_parse_embedcompattable_mismatch(self):
        self.get_instance('Specification', 'css3_backgrounds')
        content = self.good_content + '''\
<h2 id="Browser_compatibility">Browser compatibility</h2>
<div>{{EmbedCompatTable("other-slug")}}</div>
'''
        self.set_content(content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.STATUS_PARSED, fp.status, fp.get_status_display())
        self.assertFalse(fp.has_issues)
        self.assertEqual(fp.CONVERTED_MISMATCH, fp.converted_compat)

    def test_committed(self):
        self.get_instance('Section', 'background-size')  # Create existing data
        self.set_content(self.good_content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.COMMITTED_YES, fp.committed)

    def test_updated(self):
        self.get_instance('Section', 'background-size')
        spec = self.get_instance('Specification', 'css3_ui')
        content = self.good_content.replace(' </tbody>\n', '''\
   <tr>
     <td>{{SpecName('%(key)s', '#anchor', 'new section')}}</td>
     <td>{{Spec2('%(key)s')}}</td>
     <td></td>
   </tr>
 </tbody>
 ''' % {'key': spec.mdn_key})
        self.set_content(content)
        scrape_feature_page(self.page)
        fp = FeaturePage.objects.get(id=self.page.id)
        self.assertEqual(fp.COMMITTED_NEEDS_UPDATE, fp.committed)
