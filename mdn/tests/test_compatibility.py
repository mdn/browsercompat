# coding: utf-8
"""Test mdn.compatibility"""
from __future__ import unicode_literals

from django.utils.six import text_type
from parsimonious.grammar import Grammar

from mdn.compatibility import (
    compat_feature_grammar, CompatFeatureVisitor, Footnote)
from webplatformcompat.models import Feature
from .base import TestCase

feature_grammar = Grammar(compat_feature_grammar)


class TestFootnote(TestCase):
    def test_str(self):
        footnote = Footnote(raw='[1]', footnote_id='1')
        self.assertEqual('[1]', text_type(footnote))


class TestFeatureGrammar(TestCase):
    def test_standard(self):
        text = '<td>Basic Support</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed

    def test_rowspan(self):
        text = '<td rowspan="2">Two-line feature</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed

    def test_footnote(self):
        text = '<td>Bad Footnote [1]</td>'
        parsed = feature_grammar['html'].parse(text)
        assert parsed


class TestFeatureVisitor(TestCase):
    def setUp(self):
        self.parent_feature = self.get_instance(
            Feature, 'web-css-background-size')
        self.visitor = CompatFeatureVisitor(
            parent_feature=self.parent_feature)
        self.scope = 'compatibility feature'

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
