# coding: utf-8
"""Test mdn.compatibility."""
from __future__ import unicode_literals

from django.utils.six import text_type

from mdn.compatibility import (
    CellVersion, CompatFeatureVisitor, CompatFootnoteVisitor,
    CompatSectionExtractor, CompatSupportVisitor, Footnote,
    compat_feature_grammar, compat_support_grammar, compat_footnote_grammar)
from mdn.kumascript import KumaVisitor, kumascript_grammar
from webplatformcompat.models import Feature, Support
from .base import TestCase


class TestCompatSectionExtractor(TestCase):
    def setUp(self):
        self.feature = self.get_instance('Feature', 'web-css-background-size')
        self.visitor = KumaVisitor()
        self.version = self.get_instance('Version', ('firefox_desktop', '1.0'))

    def construct_html(
            self, header=None, pre_table=None, feature=None,
            browser=None, support=None, after_table=None):
        """Create a basic compatibility section."""
        return """\
{header}
{pre_table}
<div id="compat-desktop">
  <table class="compat-table">
    <tbody>
      <tr>
        <th>Feature</th>
        <th>{browser}</th>
      </tr>
      <tr>
        <td>{feature}</td>
        <td>{support}</td>
      </tr>
    </tbody>
  </table>
</div>
{after_table}
""".format(
            header=header or (
                '<h2 id="Browser_compatibility">Browser compatibility</h2>'),
            pre_table=pre_table or '<div>{{CompatibilityTable}}</div>',
            browser=browser or 'Firefox',
            feature=feature or '<code>contain</code> and <code>cover</code>',
            support=support or '1.0',
            after_table=after_table or '')

    def get_default_compat_div(self):
        browser_id = self.version.browser_id
        version_id = self.version.id
        return {
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
                'support': 'yes', 'version': version_id}]}

    def assert_extract(
            self, html, compat_divs=None, footnotes=None, issues=None,
            embedded=None):
        parsed = kumascript_grammar['html'].parse(html)
        out = self.visitor.visit(parsed)
        extractor = CompatSectionExtractor(feature=self.feature, elements=out)
        extracted = extractor.extract()
        self.assertEqual(extracted['compat_divs'], compat_divs or [])
        self.assertEqual(extracted['footnotes'], footnotes or {})
        self.assertEqual(extracted['issues'], issues or [])
        self.assertEqual(extracted['embedded'], embedded or [])

    def test_standard(self):
        html = self.construct_html()
        expected = self.get_default_compat_div()
        self.assert_extract(html, [expected])

    def test_unknown_browser(self):
        html = self.construct_html(browser='Fire')
        expected = self.get_default_compat_div()
        expected['browsers'][0] = {
            'id': '_Fire', 'name': 'Fire', 'slug': '_Fire'}
        expected['versions'][0] = {
            'id': '_Fire-1.0', 'version': '1.0', 'browser': '_Fire'}
        expected['supports'][0] = {
            'id': u'__contain and cover-_Fire-1.0',
            'support': 'yes',
            'feature': '_contain and cover',
            'version': '_Fire-1.0'}
        issue = ('unknown_browser', 205, 218, {'name': 'Fire'})
        self.assert_extract(html, [expected], issues=[issue])

    def test_wrong_first_column_header(self):
        # All known pages use "Feature" for first column, but be ready
        html = self.construct_html()
        html = html.replace('<th>Feature</th>', '<th>Features</th>')
        expected = self.get_default_compat_div()
        issue = ('feature_header', 180, 197, {'header': 'Features'})
        self.assert_extract(html, [expected], issues=[issue])

    def test_footnote(self):
        html = self.construct_html(
            support='1.0 [1]',
            after_table='<p>[1] This is a footnote.</p>')
        expected = self.get_default_compat_div()
        expected['supports'][0]['footnote'] = 'This is a footnote.'
        expected['supports'][0]['footnote_id'] = ('1', 322, 325)
        self.assert_extract(html, [expected])

    def test_footnote_mismatch(self):
        html = self.construct_html(
            support='1.0 [1]',
            after_table='<p>[2] Oops, footnote ID is wrong.</p>')
        expected = self.get_default_compat_div()
        expected['supports'][0]['footnote_id'] = ('1', 322, 325)
        footnotes = {'2': ('Oops, footnote ID is wrong.', 374, 412)}
        issues = [
            ('footnote_missing', 322, 325, {'footnote_id': '1'}),
            ('footnote_unused', 374, 412, {'footnote_id': '2'})]
        self.assert_extract(
            html, [expected], footnotes=footnotes, issues=issues)

    def test_extra_row_cell(self):
        # https://developer.mozilla.org/en-US/docs/Web/JavaScript/
        # Reference/Global_Objects/WeakSet, March 2015
        html = self.construct_html()
        html = html.replace(
            '<td>1.0</td>', '<td>1.0</td><td>{{CompatUnknown()}}</td>')
        self.assertTrue('CompatUnknown' in html)
        expected = self.get_default_compat_div()
        issue = ('extra_cell', 326, 354, {})
        self.assert_extract(html, [expected], issues=[issue])

    def test_compat_mobile_table(self):
        mobile = """
<div id="compat-mobile">
  <table class="compat-table">
    <tbody>
      <tr><th>Feature</th><th>Safari Mobile</th></tr>
      <tr>
        <td><code>contain</code> and <code>cover</code></td>
        <td>1.0 [1]</td>
      </tr>
    </tbody>
  </table>
</div>
<p></p>
<p>[1] It's really supported.</p>
"""
        html = self.construct_html(after_table=mobile)
        expected_desktop = self.get_default_compat_div()
        expected_mobile = {
            'name': 'mobile',
            'browsers': [{
                'id': '_Safari for iOS',
                'name': 'Safari for iOS',
                'slug': '_Safari for iOS',
            }],
            'features': [{
                'id': '_contain and cover',
                'name': '<code>contain</code> and <code>cover</code>',
                'slug': 'web-css-background-size_contain_and_cover',
            }],
            'versions': [{
                'id': '_Safari for iOS-1.0',
                'version': '1.0',
                'browser': '_Safari for iOS',
            }],
            'supports': [{
                'id': '__contain and cover-_Safari for iOS-1.0',
                'feature': '_contain and cover',
                'support': 'yes',
                'version': '_Safari for iOS-1.0',
                'footnote': "It's really supported.",
                'footnote_id': ('1', 581, 584),
            }],
        }
        issue = ('unknown_browser', 465, 487, {'name': 'Safari Mobile'})
        self.assert_extract(
            html, [expected_desktop, expected_mobile], issues=[issue])

    def test_pre_content(self):
        header_plus = (
            '<h2 id="Browser_compatibility">Browser compatibility</h2>'
            '<p>Here\'s some extra content.</p>')
        html = self.construct_html(header=header_plus)
        expected = self.get_default_compat_div()
        issue = ('skipped_content', 57, 90, {})
        self.assert_extract(html, [expected], issues=[issue])

    def test_feature_issue(self):
        html = self.construct_html(
            feature='<code>contain</code> and <code>cover</code> [1]')
        expected = self.get_default_compat_div()
        issue = ('footnote_feature', 300, 304, {})
        self.assert_extract(html, [expected], issues=[issue])

    def test_support_issue(self):
        html = self.construct_html(support='1.0 (or earlier)')
        expected = self.get_default_compat_div()
        issue = ('inline_text', 322, 334, {'text': '(or earlier)'})
        self.assert_extract(html, [expected], issues=[issue])

    def test_footnote_issue(self):
        html = self.construct_html(after_table="<p>Here's some text.</p>")
        expected = self.get_default_compat_div()
        issue = ('footnote_no_id', 370, 394, {})
        self.assert_extract(html, [expected], issues=[issue])

    def test_table_div_wraps_h3(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode
        html = self.construct_html()
        html = html.replace(
            '</div>', '<h3>Gecko Notes</h3><p>It rocks</p></div>')
        expected = self.get_default_compat_div()
        issues = [
            ('skipped_content', 58, 126, {}),
            ('footnote_gap', 434, 438, {}),
            ('footnote_no_id', 418, 433, {})]
        self.assert_extract(html, [expected], issues=issues)

    def test_support_colspan_exceeds_table_width(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
        html = self.construct_html()
        html = html.replace('<td>1.0', '<td colspan="2">1.0')
        expected = self.get_default_compat_div()
        issue = ('cell_out_of_bounds', 314, 338, {})
        self.assert_extract(html, [expected], issues=[issue])

    def test_embedded(self):
        html = self.construct_html(
            after_table="<div>{{EmbedCompatTable('foo-bar')}}</div>")
        expected = self.get_default_compat_div()
        self.assert_extract(html, [expected], embedded=['foo-bar'])


class TestFootnote(TestCase):
    def test_numeric(self):
        footnote = Footnote(raw='[1]', footnote_id='1')
        self.assertEqual('[1]', text_type(footnote))
        self.assertEqual('1', footnote.footnote_id)
        self.assertEqual('1', footnote.raw_footnote)

    def test_stars(self):
        # TODO: replace "convert to '3'" with raw '***'
        footnote = Footnote(raw='[***]', footnote_id='***')
        self.assertEqual('[3]', text_type(footnote))
        self.assertEqual('3', footnote.footnote_id)
        self.assertEqual('***', footnote.raw_footnote)


class TestFeatureGrammar(TestCase):
    def test_standard(self):
        text = '<td>contain and cover</td>'
        parsed = compat_feature_grammar['html'].parse(text)
        assert parsed

    def test_rowspan(self):
        text = '<td rowspan="2">Two-line feature</td>'
        parsed = compat_feature_grammar['html'].parse(text)
        assert parsed

    def test_cell_with_footnote(self):
        text = '<td>Bad Footnote [1]</td>'
        parsed = compat_feature_grammar['html'].parse(text)
        assert parsed


class TestFeatureVisitor(TestCase):
    scope = 'compatibility feature'

    def setUp(self):
        self.parent_feature = self.get_instance(
            'Feature', 'web-css-background-size')
        self.visitor = CompatFeatureVisitor(parent_feature=self.parent_feature)

    def assert_feature(
            self, contents, feature_id, name, slug, canonical=False,
            experimental=False, standardized=True, obsolete=False,
            issues=None):
        row_cell = '<td>%s</td>' % contents
        parsed = compat_feature_grammar['html'].parse(row_cell)
        self.visitor.visit(parsed)
        feature_dict = self.visitor.to_feature_dict()
        self.assertEqual(issues or [], self.visitor.issues)
        self.assertEqual(feature_id, feature_dict['id'])
        self.assertEqual(slug, feature_dict['slug'])
        self.assertEqual(name, feature_dict['name'])
        if canonical:
            self.assertTrue(feature_dict['canonical'])
        else:
            self.assertFalse('canonical' in feature_dict)
        if experimental:
            self.assertTrue(feature_dict['experimental'])
        else:
            self.assertFalse('experimental' in feature_dict)
        if obsolete:
            self.assertTrue(feature_dict['obsolete'])
        else:
            self.assertFalse('obsolete' in feature_dict)
        if standardized:
            self.assertFalse('standardized' in feature_dict)
        else:
            self.assertFalse(feature_dict['standardized'])

    def test_remove_whitespace(self):
        cell = (
            ' Support for<br>\n     <code>contain</code> and'
            ' <code>cover</code> ')
        feature_id = '_support for contain and cover'
        name = 'Support for <code>contain</code> and <code>cover</code>'
        slug = 'web-css-background-size_support_for_contain_and_co'
        self.assert_feature(cell, feature_id, name, slug)

    def test_code_sequence(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/display
        cell = (
            '<code>none</code>, <code>inline</code> and'
            ' <code>block</code>')
        feature_id = '_none, inline and block'
        name = '<code>none</code>, <code>inline</code> and <code>block</code>'
        slug = 'web-css-background-size_none_inline_and_block'
        self.assert_feature(cell, feature_id, name, slug)

    def test_canonical(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/display
        cell = '<code>list-item</code>'
        feature_id = '_list-item'
        name = 'list-item'
        slug = 'web-css-background-size_list-item'
        self.assert_feature(cell, feature_id, name, slug, canonical=True)

    def test_canonical_match(self):
        name = 'list-item'
        slug = 'slug-list-item'
        feature = self.create(
            Feature, parent=self.parent_feature, name={'zxx': name}, slug=slug)
        cell = '<code>list-item</code>'
        self.assert_feature(cell, feature.id, name, slug, canonical=True)

    def test_ks_experimental(self):
        cell = '<code>grid</code> {{experimental_inline}}'
        feature_id = '_grid'
        name = 'grid'
        slug = 'web-css-background-size_grid'
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, experimental=True)

    def test_ks_non_standard_inline(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AnimationEvent
        cell = '<code>initAnimationEvent()</code> {{non-standard_inline}}'
        feature_id = '_initanimationevent()'
        name = 'initAnimationEvent()'
        slug = 'web-css-background-size_initanimationevent'
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, standardized=False)

    def test_ks_deprecated_inline(self):
        cell = '<code>initAnimationEvent()</code> {{deprecated_inline}}'
        feature_id = '_initanimationevent()'
        name = 'initAnimationEvent()'
        slug = 'web-css-background-size_initanimationevent'
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, obsolete=True)

    def test_ks_obsolete_inline(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
        cell = 'Version -76 support {{obsolete_inline}}'
        feature_id = '_version -76 support'
        name = 'Version -76 support'
        slug = 'web-css-background-size_version_-76_support'
        self.assert_feature(cell, feature_id, name, slug, obsolete=True)

    def test_ks_htmlelement(self):
        cell = '{{ HTMLElement("progress") }}'
        feature_id = '_progress'
        name = '&lt;progress&gt;'
        slug = 'web-css-background-size_progress'
        self.assert_feature(cell, feature_id, name, slug, canonical=True)

    def test_ks_domxref(self):
        cell = '{{domxref("DeviceProximityEvent")}}'
        feature_id = '_deviceproximityevent'
        name = 'DeviceProximityEvent'
        slug = 'web-css-background-size_deviceproximityevent'
        self.assert_feature(cell, feature_id, name, slug, canonical=True)

    def test_unknown_kumascript(self):
        cell = 'feature foo {{bar}}'
        feature_id = '_feature foo'
        name = 'feature foo'
        slug = 'web-css-background-size_feature_foo'
        issue = ('unknown_kumascript', 16, 23,
                 {'name': 'bar', 'args': [], 'kumascript': '{{bar}}',
                  'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])

    def test_nonascii_name(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant
        cell = '<code>ß</code> → <code>SS</code>'
        feature_id = '_\xdf \u2192 ss'
        name = '<code>\xdf</code> \u2192 <code>SS</code>'
        slug = 'web-css-background-size_ss'
        self.assert_feature(cell, feature_id, name, slug)

    def test_footnote(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-align
        cell = 'Block alignment values [1] {{not_standard_inline}}'
        feature_id = '_block alignment values'
        name = 'Block alignment values'
        slug = 'web-css-background-size_block_alignment_values'
        issue = ('footnote_feature', 27, 31, {})
        self.assert_feature(
            cell, feature_id, name, slug, standardized=False, issues=[issue])

    def test_bracket(self):
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input
        cell = 'accept=[file extension]'
        feature_id = '_accept=[file extension]'
        name = 'accept=[file extension]'
        slug = 'web-css-background-size_accept_file_extension'
        self.assert_feature(cell, feature_id, name, slug)

    def test_digit(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/transform
        cell = '3D Support'
        feature_id = '_3d support'
        name = '3D Support'
        slug = 'web-css-background-size_3d_support'
        self.assert_feature(cell, feature_id, name, slug)

    def test_link(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/EventSource
        cell = ('<a href="/En/HTTP_access_control">'
                'Cross-Origin Resource Sharing</a><br>')
        feature_id = '_cross-origin resource sharing'
        name = 'Cross-Origin Resource Sharing'
        slug = 'web-css-background-size_cross-origin_resource_shar'
        issue = (
            'tag_dropped', 4, 38, {'tag': 'a', 'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])

    def test_p(self):
        # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const
        cell = '<p>Reassignment fails</p>'
        feature_id = '_reassignment fails'
        name = 'Reassignment fails'
        slug = 'web-css-background-size_reassignment_fails'
        issue = ('tag_dropped', 4, 7, {'tag': 'p', 'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])

    def test_span(self):
        cell = '<span class="strong">Strong</span>'
        feature_id = '_strong'
        name = 'Strong'
        slug = 'web-css-background-size_strong'
        issue = ('tag_dropped', 4, 25, {'tag': 'span', 'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])

    def test_table(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack
        cell = """\
<table class="compat-table">
  <tbody>
    <tr>
      <td><code>.stop()</code></td>
    </tr>
  </tbody>
</table>"""
        feature_id = '_.stop()'
        name = '.stop()'
        slug = 'web-css-background-size_stop'
        issues = [
            ('tag_dropped', 4, 32, {'tag': 'table', 'scope': self.scope}),
            ('tag_dropped', 35, 42, {'tag': 'tbody', 'scope': self.scope}),
            ('tag_dropped', 47, 51, {'tag': 'tr', 'scope': self.scope}),
            ('tag_dropped', 58, 62, {'tag': 'td', 'scope': self.scope})]
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, issues=issues)


class TestSupportGrammar(TestCase):
    def assert_version(self, text, version, eng_version=None):
        ws1, version_node, ws2 = (
            compat_support_grammar['cell_version'].parse(text))
        match = version_node.match.groupdict()
        expected = {'version': version, 'eng_version': eng_version}
        self.assertEqual(expected, match)

    def test_version_number(self):
        self.assert_version('1', version='1')

    def test_cell_version_number_dotted(self):
        self.assert_version('1.0', version='1.0')

    def test_cell_version_number_spaces(self):
        self.assert_version('1 ', version='1')

    def test_cell_version_number_dotted_spaces(self):
        self.assert_version('1.0\n\t', version='1.0')

    def test_cell_version_number_with_engine(self):
        self.assert_version('1.0 (85)', version='1.0', eng_version='85')

    def test_cell_version_number_with_dotted_engine(self):
        self.assert_version('5.0 (532.5)', version='5.0', eng_version='532.5')

    def assert_no_prefix(self, text):
        node = compat_support_grammar['cell_noprefix'].parse(text)
        self.assertEqual(text, node.text)

    def test_unprefixed(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AudioContext.createBufferSource
        self.assert_no_prefix(' (unprefixed) ')

    def test_noprefix(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Navigator.vibrate
        self.assert_no_prefix(' (no prefix) ')

    def test_without_prefix_naked(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-line
        self.assert_no_prefix('without prefix')

    def test_without_prefix(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/BatteryManager
        self.assert_no_prefix(' (without prefix) ')

    def assert_partial(self, text):
        node = compat_support_grammar['cell_partial'].parse(text)
        self.assertEqual(text, node.text)

    def test_comma_partial(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/IDBCursor
        self.assert_partial(', partial')

    def test_parens_partal(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration
        self.assert_partial('(partial)')


class TestCompatVersion(TestCase):
    def test_dotted(self):
        version = CellVersion(raw='1.0', version='1.0')
        self.assertEqual('1.0', version.version)
        self.assertEqual('1.0', text_type(version))

    def test_plain(self):
        version = CellVersion(raw='1', version='1')
        self.assertEqual('1.0', version.version)
        self.assertEqual('1.0', text_type(version))

    def test_with_engine(self):
        version = CellVersion(
            raw='1.0 (85)', version='1.0', engine_version='85')
        self.assertEqual('1.0', version.version)
        self.assertEqual('1.0 (85)', text_type(version))


class TestSupportVisitor(TestCase):
    scope = 'compatibility support'

    def setUp(self):
        self.feature_id = '_feature'
        self.browser_id = '_browser'
        self.browser_name = 'Browser'
        self.browser_slug = 'browser'

    def set_browser(self, browser):
        self.browser_id = browser.id
        self.browser_name = browser.name
        self.browser_slug = browser.slug

    def assert_support(
            self, contents, expected_versions=None, expected_supports=None,
            issues=None):
        row_cell = '<td>%s</td>' % contents
        parsed = compat_support_grammar['html'].parse(row_cell)
        self.visitor = CompatSupportVisitor(
            self.feature_id, self.browser_id, self.browser_name,
            self.browser_slug)
        self.visitor.visit(parsed)
        expected_versions = expected_versions or []
        expected_supports = expected_supports or []
        self.assertEqual(len(expected_versions), len(expected_supports))
        for version, support in zip(expected_versions, expected_supports):
            if 'id' not in version:
                version['id'] = '_{}-{}'.format(
                    self.browser_name, version['version'])
            version['browser'] = self.browser_id

            if 'id' not in support:
                support['id'] = '_{}-{}'.format(self.feature_id, version['id'])
            support['version'] = version['id']
            support['feature'] = self.feature_id
        self.assertEqual(expected_versions, self.visitor.versions)
        self.assertEqual(expected_supports, self.visitor.supports)
        self.assertEqual(issues or [], self.visitor.issues)

    def test_version(self):
        self.assert_support('1.0', [{'version': '1.0'}], [{'support': 'yes'}])

    def test_version_matches(self):
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        self.set_browser(version.browser)
        self.assert_support(
            '1.0', [{'version': '1.0', 'id': version.id}],
            [{'support': 'yes'}])

    def test_new_version_existing_browser(self):
        browser = self.get_instance('Browser', 'firefox_desktop')
        self.set_browser(browser)
        issue = (
            'unknown_version', 4, 7,
            {'browser_id': browser.id,
             'browser_name': {'en': 'Firefox for Desktop'},
             'browser_slug': 'firefox_desktop', 'version': '2.0'})
        self.assert_support(
            '2.0', [{'version': '2.0'}], [{'support': 'yes'}], issues=[issue])

    def test_support_matches(self):
        version = self.get_instance('Version', ('firefox_desktop', '1.0'))
        self.set_browser(version.browser)
        feature = self.get_instance(
            'Feature', 'web-css-background-size-contain_and_cover')
        self.feature_id = feature.id
        support = self.create(Support, version=version, feature=feature)
        self.assert_support(
            '1.0',
            [{'version': '1.0', 'id': version.id}],
            [{'support': 'yes', 'id': support.id}])

    def test_compatno(self):
        self.assert_support(
            '{{CompatNo}}',
            [{'version': 'current'}], [{'support': 'no'}])

    def test_compatversionunknown(self):
        self.assert_support(
            '{{CompatVersionUnknown}}',
            [{'version': 'current'}], [{'support': 'yes'}])

    def test_compatunknown(self):
        self.assert_support('{{CompatUnknown}}', [], [])

    def test_compatgeckodesktop(self):
        self.assert_support(
            '{{CompatGeckoDesktop("1")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_compatgeckodesktop_bad_num(self):
        self.assert_support(
            '{{CompatGeckoDesktop("1.1")}}',
            issues=[('compatgeckodesktop_unknown', 4, 33, {'version': '1.1'})])

    def test_compatgeckofxos(self):
        self.assert_support(
            '{{CompatGeckoFxOS("7")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_compatgeckofxos_bad_version(self):
        self.assert_support(
            '{{CompatGeckoFxOS("999999")}}',
            issues=[('compatgeckofxos_unknown', 4, 33, {'version': '999999'})])

    def test_compatgeckofxos_bad_override(self):
        self.assert_support(
            '{{CompatGeckoFxOS("18","5.0")}}',
            issues=[('compatgeckofxos_override', 4, 35,
                     {'override': '5.0', 'version': '18'})])

    def test_compatgeckomobile(self):
        self.assert_support(
            '{{CompatGeckoMobile("1")}}',
            [{'version': '1.0'}], [{'support': 'yes'}])

    def test_compatandroid(self):
        self.assert_support(
            '{{CompatAndroid("3.0")}}',
            [{'version': '3.0'}], [{'support': 'yes'}])

    def test_compatnightly(self):
        self.assert_support(
            '{{CompatNightly}}',
            [{'version': 'nightly'}], [{'support': 'yes'}])

    def test_unknown_kumascript(self):
        issues = [(
            'unknown_kumascript', 4, 19,
            {'name': 'UnknownKuma', 'args': [],
             'scope': 'compatibility support',
             'kumascript': '{{UnknownKuma}}'})]
        self.assert_support('{{UnknownKuma}}', issues=issues)

    def test_with_prefix_and_break(self):
        self.assert_support(
            ('{{CompatVersionUnknown}}{{property_prefix("-webkit")}}<br>\n'
             '   2.3'),
            [{'version': 'current'}, {'version': '2.3'}],
            [{'support': 'yes', 'prefix': '-webkit'}, {'support': 'yes'}])

    def test_p_tags(self):
        self.assert_support(
            '<p>4.0</p><p>32</p>',
            [{'version': '4.0'}, {'version': '32.0'}],
            [{'support': 'yes'}, {'support': 'yes'}])

    def test_two_line_note(self):
        self.assert_support(
            '18<br>\n(behind a pref) [1]',
            [{'version': '18.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 27, 30)}],
            issues=[('inline_text', 10, 27, {'text': '(behind a pref)'})])

    def test_removed_in_gecko(self):
        self.assert_support(
            ('{{ CompatGeckoMobile("6.0") }}<br>'
             'Removed in {{ CompatGeckoMobile("23.0") }}'),
            [{'version': '6.0'}, {'version': '23.0'}],
            [{'support': 'yes'}, {'support': 'no'}])

    def test_multi_br(self):
        self.assert_support(
            ('{{ CompatGeckoMobile("6.0") }}<br><br>'
             'Removed in {{ CompatGeckoMobile("23.0") }}'),
            [{'version': '6.0'}, {'version': '23.0'}],
            [{'support': 'yes'}, {'support': 'no'}])

    def test_removed_in_version(self):
        self.assert_support(
            'Removed in 32',
            [{'version': '32.0'}], [{'support': 'no'}])

    def test_unprefixed(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AudioContext.createBufferSource
        self.assert_support(
            '32 (unprefixed)',
            [{'version': '32.0'}], [{'support': 'yes'}])

    def test_partial(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/IDBCursor
        self.assert_support(
            '10, partial',
            [{'version': '10.0'}], [{'support': 'partial'}])

    def test_unmatched_free_text(self):
        self.assert_support(
            '32 (or earlier)',
            [{'version': '32.0'}], [{'support': 'yes'}],
            issues=[('inline_text', 7, 19, {'text': '(or earlier)'})])

    def test_code_block(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/order
        self.assert_support(
            '32 with alt name <code>foobar</code>',
            [{'version': '32.0'}], [{'support': 'yes'}],
            issues=[
                ('inline_text', 7, 21, {'text': 'with alt name'}),
                ('inline_text', 21, 40, {'text': '<code>foobar</code>'})])

    def test_spaces(self):
        self.assert_support('  ')

    def test_prefix_plus_footnote(self):
        self.assert_support(
            '18{{property_prefix("-webkit")}} [1]',
            [{'version': '18.0'}],
            [{'support': 'partial', 'prefix': '-webkit',
              'footnote_id': ('1', 37, 40)}])

    def test_prefix_double_footnote(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/CSSSupportsRule
        self.assert_support(
            '{{ CompatGeckoDesktop("17") }} [1][2]',
            [{'version': '17.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 35, 38)}],
            issues=[('footnote_multiple', 38, 41,
                     {'prev_footnote_id': '1', 'footnote_id': '2'})])

    def test_double_footnote_link_sup(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/flex
        self.assert_support(
            '{{CompatGeckoDesktop("20.0")}} '
            '<sup><a href="#bc2">[2]</a><a href="#bc3">[3]</a></sup>',
            [{'version': '20.0'}],
            [{'support': 'yes', 'footnote_id': ('2', 55, 58)}],
            issues=[('footnote_multiple', 77, 80,
                    {'prev_footnote_id': '2', 'footnote_id': '3'})])

    def test_star_footnote(self):
        # TODO: use raw footnote once footnote section is converted
        self.assert_support(
            '{{CompatGeckoDesktop("20.0")}} [***]',
            [{'version': '20.0'}],
            [{'support': 'yes', 'footnote_id': ('3', 35, 40)}])

    def test_nbsp(self):
        self.assert_support(
            '15&nbsp;{{property_prefix("webkit")}}',
            [{'version': '15.0'}], [{'support': 'yes', 'prefix': 'webkit'}])

    def test_other_kumascript(self):
        issue = (
            'unexpected_kumascript', 7, 30,
            {'kumascript': '{{experimental_inline}}',
             'name': 'experimental_inline', 'args': [], 'scope': self.scope,
             'expected_scopes': 'compatibility feature'})
        self.assert_support(
            '22 {{experimental_inline}}',
            [{'version': '22.0'}], [{'support': 'yes'}], issues=[issue])

    def test_multiversion_prefix_no(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Text/replaceWholeText
        self.assert_support(
            '{{CompatVersionUnknown}} [1] <br> 30.0 <br> {{CompatNo}} 41.0',
            [{'version': 'current'}, {'version': '30.0'}, {'version': '41.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 29, 33)},
             {'support': 'yes'}, {'support': 'no'}])

    def test_multiversion_suffix_no(self):
        self.assert_support(
            '{{CompatVersionUnknown}} [1] <br> 30.0 <br> 41.0 {{CompatNo}}',
            [{'version': 'current'}, {'version': '30.0'}, {'version': '41.0'}],
            [{'support': 'yes', 'footnote_id': ('1', 29, 33)},
             {'support': 'yes'}, {'support': 'no'}])


class TestFootnoteGrammar(TestCase):
    def test_footnote_paragraph(self):
        footnotes = '<p>[2] A footnote</p>'
        parsed = compat_footnote_grammar['html'].parse(footnotes)
        self.assertEqual(footnotes, parsed.text)


class TestFootnoteVisitor(TestCase):
    scope = 'compatibility footnote'

    def setUp(self):
        self.visitor = CompatFootnoteVisitor()

    def assert_footnotes(self, content, expected, issues=None, embedded=None):
        parsed = compat_footnote_grammar['html'].parse(content)
        self.visitor.visit(parsed)
        footnotes = self.visitor.finalize_footnotes()
        self.assertEqual(expected, footnotes)
        self.assertEqual(issues or [], self.visitor.issues)
        self.assertEqual(embedded or [], self.visitor.embedded)

    def test_empty(self):
        footnotes = '\n'
        expected = {}
        self.assert_footnotes(footnotes, expected)

    def test_simple(self):
        footnotes = '<p>[1] A footnote.</p>'
        expected = {'1': ('A footnote.', 0, 22)}
        self.assert_footnotes(footnotes, expected)

    def test_multi_paragraph(self):
        footnotes = '<p>[1] Footnote line 1.</p><p>Footnote line 2.</p>'
        expected = {
            '1': ('<p>Footnote line 1.</p>\n<p>Footnote line 2.</p>', 0, 50)}
        self.assert_footnotes(footnotes, expected)

    def test_multiple_footnotes(self):
        footnotes = '<p>[1] Footnote 1.</p><p>[2] Footnote 2.</p>'
        expected = {'1': ('Footnote 1.', 0, 22), '2': ('Footnote 2.', 22, 44)}
        self.assert_footnotes(footnotes, expected)

    def test_kumascript_cssxref(self):
        footnotes = '<p>[1] Use {{cssxref("-moz-border-image")}}</p>'
        expected = {
            '1': (
                'Use <a href="https://developer.mozilla.org/en-US/docs/Web/'
                'CSS/-moz-border-image"><code>-moz-border-image</code></a>',
                0, 47)}
        self.assert_footnotes(footnotes, expected)

    def test_unknown_kumascriptscript(self):
        footnotes = (
            '<p>[1] Footnote {{UnknownKuma}} but the beat continues.</p>')
        expected = {'1': ('Footnote but the beat continues.', 0, 59)}
        issue = (
            'unknown_kumascript', 16, 32,
            {'name': 'UnknownKuma', 'args': [], 'scope': 'footnote',
             'kumascript': '{{UnknownKuma}}'})
        self.assert_footnotes(footnotes, expected, issues=[issue])

    def test_pre_section(self):
        footnotes = '<p>[1] Here\'s some code:</p><pre>foo = bar</pre>'
        expected = {
            '1': ("<p>Here's some code:</p>\n<pre>foo = bar</pre>", 0, 48)}
        self.assert_footnotes(footnotes, expected)

    def test_pre_without_footnotes(self):
        footnotes = '<p>Here\'s some code:</p><pre>foo = bar</pre>'
        issues = [
            ('footnote_no_id', 0, 24, {}),
            ('footnote_no_id', 24, 44, {})]
        self.assert_footnotes(footnotes, {}, issues)

    def test_pre_with_attrs_section(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/white-space
        footnotes = (
            '<p>[1] Here\'s some code:</p>\n'
            '<pre class="brush:css">\n'
            '.foo {background-image: url(bg-image.png);}\n'
            '</pre>')
        expected = {
            '1': (
                "<p>Here's some code:</p>\n<pre>\n"
                '.foo {background-image: url(bg-image.png);}\n</pre>',
                0, 103)}
        issue = (
            'unexpected_attribute', 34, 51,
            {'ident': 'class', 'node_type': 'pre', 'value': 'brush:css',
             'expected': 'no attributes'})
        self.assert_footnotes(footnotes, expected, issues=[issue])

    def test_asterisk(self):
        footnotes = '<p>[*] A footnote</p>'
        expected = {'1': ('A footnote', 0, 21)}
        self.assert_footnotes(footnotes, expected)

    def test_bad_footnote(self):
        footnotes = '<p>A footnote.</p>'
        issue = ('footnote_no_id', 0, 18, {})
        self.assert_footnotes(footnotes, {}, issues=[issue])

    def test_bad_footnote_prefix(self):
        footnotes = '<p>Footnote [1] - The content.</p>'
        expected = {'1': ('- The content.', 16, 30)}
        issue = ('footnote_no_id', 3, 12, {})
        self.assert_footnotes(footnotes, expected, issues=[issue])

    def test_bad_footnote_unknown_kumascript(self):
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/color-profile
        footnotes = '<p>{{SVGRef}}</p>'
        issue = (
            'unknown_kumascript', 3, 13,
            {'name': 'SVGRef', 'args': [], 'kumascript': '{{SVGRef}}',
             'scope': u'footnote'})
        self.assert_footnotes(footnotes, {}, issues=[issue])

    def test_empty_paragraph_no_footnotes(self):
        footnotes = ('<p>  </p>\n')
        self.assert_footnotes(footnotes, {})

    def test_empty_paragraph_invalid_footnote(self):
        footnotes = (
            '<p> </p>\n'
            '<p>Invalid footnote.</p>\n'
            '<p>  </p>')
        issue = ('footnote_no_id', 9, 33, {})
        self.assert_footnotes(footnotes, {}, issues=[issue])
        self.assertEqual(footnotes[9:33], '<p>Invalid footnote.</p>')

    def test_empty_paragraphs_trimmed(self):
        footnote = (
            '<p> </p>\n'
            '<p>[1] Valid footnote.</p>'
            '<p>   </p>'
            '<p>Continues footnote 1.</p>')
        expected = {
            '1': (
                '<p>Valid footnote.</p>\n<p>Continues footnote 1.</p>',
                9, 73)}
        self.assert_footnotes(footnote, expected)

    def test_code(self):
        footnote = (
            '<p>[1] From Firefox 31 to 35, <code>will-change</code>'
            ' was available...</p>')
        expected = {
            '1': (
                'From Firefox 31 to 35, <code>will-change</code>'
                ' was available...', 0, 75)}
        self.assert_footnotes(footnote, expected)

    def test_span(self):
        # https://developer.mozilla.org/en-US/docs/Web/Events/DOMContentLoaded
        footnote = (
            '<p>[1]<span style="font-size: 14px; line-height: 18px;">'
            'Bubbling for this event is supported by at least Gecko 1.9.2,'
            ' Chrome 6, and Safari 4.</span></p>')
        expected = {
            '1': ('Bubbling for this event is supported by at least Gecko'
                  ' 1.9.2, Chrome 6, and Safari 4.', 0, 152)}
        issue = ('tag_dropped', 6, 56, {'scope': 'footnote', 'tag': 'span'})
        self.assert_footnotes(footnote, expected, issues=[issue])

    def test_a(self):
        # https://developer.mozilla.org/en-US/docs/Web/SVG/SVG_as_an_Image
        footnote = (
            '<p>[1] Compatibility data from'
            '<a href="http://caniuse.com" title="http://caniuse.com">'
            'caniuse.com</a>.</p>')
        expected = {
            '1': ('Compatibility data from <a href="http://caniuse.com">'
                  'caniuse.com</a>.', 0, 106)}
        self.assert_footnotes(footnote, expected)

    def test_br_start(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/VRFieldOfViewReadOnly/downDegrees
        footnote = "<p><br>\n[1] To find information on Chrome's WebVR...</p>"
        expected = {'1': ("To find information on Chrome's WebVR...", 0, 56)}
        self.assert_footnotes(footnote, expected)

    def test_br_end(self):
        # https://developer.mozilla.org/en-US/docs/Web/Events/wheel
        footnote = "<p>[1] Here's a footnote. <br></p>"
        expected = {'1': ("Here's a footnote.", 0, 34)}
        self.assert_footnotes(footnote, expected)

    def test_br_footnotes(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/URLUtils/hash
        footnote = '<p>[1] Footnote 1.<br>[2] Footnote 2.</p>'
        expected = {'1': ('Footnote 1.', 7, 18), '2': ('Footnote 2.', 26, 37)}
        self.assert_footnotes(footnote, expected)

    def test_embedcompattable(self):
        footnote = '<div>{{EmbedCompatTable("foo")}}</div>'
        self.assert_footnotes(footnote, {}, embedded=['foo'])
