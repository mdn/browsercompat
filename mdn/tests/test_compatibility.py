# coding: utf-8
"""Test mdn.compatibility"""
from __future__ import unicode_literals

from django.utils.six import text_type
from parsimonious.grammar import Grammar

from mdn.compatibility import (
    compat_feature_grammar, compat_support_grammar, CellVersion,
    CompatFeatureVisitor, CompatSupportVisitor, Footnote)
from webplatformcompat.models import Browser, Feature, Support, Version
from .base import TestCase

feature_grammar = Grammar(compat_feature_grammar)
support_grammar = Grammar(compat_support_grammar)


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
        text = '<td>Basic Support</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed

    def test_rowspan(self):
        text = '<td rowspan="2">Two-line feature</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed

    def test_cell_with_footnote(self):
        text = '<td>Bad Footnote [1]</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed


class TestFeatureVisitor(TestCase):
    scope = 'compatibility feature'

    def setUp(self):
        self.parent_feature = self.get_instance(
            Feature, 'web-css-background-size')
        self.visitor = CompatFeatureVisitor(parent_feature=self.parent_feature)

    def assert_feature(
            self, contents, feature_id, name, slug, canonical=False,
            experimental=False, standardized=True, obsolete=False,
            issues=None):
        row_cell = "<td>%s</td>" % contents
        parsed = feature_grammar['html'].parse(row_cell)
        self.visitor.visit(parsed)
        self.assertEqual(self.visitor.feature_id, feature_id)
        self.assertEqual(self.visitor.slug, slug)
        self.assertEqual(self.visitor.name, name)
        self.assertEqual(self.visitor.canonical, canonical)
        self.assertEqual(self.visitor.experimental, experimental)
        self.assertEqual(self.visitor.standardized, standardized)
        self.assertEqual(self.visitor.obsolete, obsolete)
        self.assertEqual(issues or [], self.visitor.issues)
        feature_dict = self.visitor.to_feature_dict()
        self.assertEqual(self.visitor.feature_id, feature_dict['id'])
        self.assertEqual(self.visitor.slug, feature_dict['slug'])
        self.assertEqual(self.visitor.name, feature_dict['name'])
        if self.visitor.canonical:
            self.assertTrue(feature_dict['canonical'])
        else:
            self.assertFalse('canonical' in feature_dict)
        if self.visitor.experimental:
            self.assertTrue(feature_dict['experimental'])
        else:
            self.assertFalse('experimental' in feature_dict)
        if self.visitor.obsolete:
            self.assertTrue(feature_dict['obsolete'])
        else:
            self.assertFalse('obsolete' in feature_dict)
        if self.visitor.standardized:
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
        slug = 'web-css-background-size_initanimationevent_'
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, standardized=False)

    def test_ks_deprecated_inline(self):
        cell = '<code>initAnimationEvent()</code> {{deprecated_inline}}'
        feature_id = '_initanimationevent()'
        name = 'initAnimationEvent()'
        slug = 'web-css-background-size_initanimationevent_'
        self.assert_feature(
            cell, feature_id, name, slug, canonical=True, obsolete=True)

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
        issue = ('footnote_feature', 27, 30, {})
        self.assert_feature(
            cell, feature_id, name, slug, standardized=False, issues=[issue])

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
        issue = ('tag_dropped', 4, 71, {'tag': 'a', 'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])

    def test_p(self):
        # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const
        cell = '<p>Reassignment fails</p>'
        feature_id = '_reassignment fails'
        name = 'Reassignment fails'
        slug = 'web-css-background-size_reassignment_fails'
        issue = ('tag_dropped', 4, 29, {'tag': 'p', 'scope': self.scope})
        self.assert_feature(cell, feature_id, name, slug, issues=[issue])


class TestSupportGrammar(TestCase):
    def assert_version(self, text, version, eng_version=None):
        match = support_grammar["cell_version"].parse(text).match.groupdict()
        expected = {"version": version, "eng_version": eng_version}
        self.assertEqual(expected, match)

    def test_version_number(self):
        self.assert_version("1", version="1")

    def test_cell_version_number_dotted(self):
        self.assert_version("1.0", version="1.0")

    def test_cell_version_number_spaces(self):
        self.assert_version("1 ", version="1")

    def test_cell_version_number_dotted_spaces(self):
        self.assert_version("1.0\n\t", version="1.0")

    def test_cell_version_number_with_engine(self):
        self.assert_version("1.0 (85)", version="1.0", eng_version="85")

    def test_cell_version_number_with_dotted_engine(self):
        self.assert_version("5.0 (532.5)", version="5.0", eng_version="532.5")

    def assert_no_prefix(self, text):
        node = support_grammar["cell_noprefix"].parse(text)
        self.assertEqual(text, node.text)

    def test_unprefixed(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/AudioContext.createBufferSource
        self.assert_no_prefix(" (unprefixed) ")

    def test_noprefix(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/Navigator.vibrate
        self.assert_no_prefix(" (no prefix) ")

    def test_without_prefix_naked(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-line
        self.assert_no_prefix("without prefix")

    def test_without_prefix(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/BatteryManager
        self.assert_no_prefix(" (without prefix) ")

    def assert_partial(self, text):
        node = support_grammar['cell_partial'].parse(text)
        self.assertEqual(text, node.text)

    def test_comma_partial(self):
        # https://developer.mozilla.org/en-US/docs/Web/API/IDBCursor
        self.assert_partial(", partial")

    def test_parens_partal(self):
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration
        self.assert_partial("(partial)")


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
        row_cell = "<td>%s</td>" % contents
        parsed = support_grammar['html'].parse(row_cell)
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
        version = self.get_instance(Version, ('firefox', '1.0'))
        self.set_browser(version.browser)
        self.assert_support(
            '1.0', [{'version': '1.0', 'id': version.id}],
            [{'support': 'yes'}])

    def test_new_version_existing_browser(self):
        browser = self.get_instance(Browser, 'firefox')
        self.set_browser(browser)
        issue = (
            'unknown_version', 4, 7,
            {'browser_id': 1, 'browser_name': {"en": "Firefox"},
             'browser_slug': 'firefox', 'version': '2.0'})
        self.assert_support(
            '2.0', [{'version': '2.0'}], [{'support': 'yes'}], issues=[issue])

    def test_support_matches(self):
        version = self.get_instance(Version, ('firefox', '1.0'))
        self.set_browser(version.browser)
        feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
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
             'kumascript': "{{UnknownKuma}}"})]
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
            issues=[('inline_text', 11, 27, {'text': '(behind a pref)'})])

    def test_removed_in_gecko(self):
        self.assert_support(
            ('{{ CompatGeckoMobile("6.0") }}<br>'
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
            'unknown_kumascript', 7, 30,
            {'kumascript': '{{experimental_inline}}',
             'name': 'experimental_inline', 'args': [], 'scope': self.scope})
        self.assert_support(
            '22 {{experimental_inline}}',
            [{'version': '22.0'}], [{'support': 'yes'}], issues=[issue])
