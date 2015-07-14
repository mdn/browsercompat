# coding: utf-8
"""Test mdn.data"""
from __future__ import unicode_literals

from mdn.data import Data
from webplatformcompat.models import (
    Browser, Feature, Specification, Support, Version)
from .base import TestCase


class TestDataBase(TestCase):
    def setUp(self):
        self.data = Data()


class TestDataSpecificationByKey(TestDataBase):
    def assert_specification_by_key(self, key, expected):
        with self.assertNumQueries(1):
            self.assertEqual(self.data.specification_by_key(key), expected)
        with self.assertNumQueries(0):
            self.assertEqual(self.data.specification_by_key(key), expected)

    def test_missing(self):
        self.assert_specification_by_key('NoSpec', None)

    def test_found(self):
        spec = self.get_instance(Specification, 'css3_backgrounds')
        self.assert_specification_by_key(spec.mdn_key, spec)


class TestDataFeatureParamsByName(TestDataBase):
    def setUp(self):
        super(TestDataFeatureParamsByName, self).setUp()
        self.parent = self.get_instance(Feature, 'web-css-background-size')

    def assert_feature_params_by_name(self, name, feature, f_id, slug):
        params = self.data.feature_params_by_name(self.parent, name)
        self.assertEqual(params.feature, feature)
        self.assertEqual(params.feature_id, f_id)
        self.assertEqual(params.slug, slug)
        with self.assertNumQueries(0):
            new_params = self.data.feature_params_by_name(self.parent, name)
        self.assertEqual(params, new_params)

    def test_feature_params_by_name_new(self):
        self.assert_feature_params_by_name(
            'Basic Support', None, '_basic support',
            'web-css-background-size_basic_support')

    def test_feature_params_by_name_match(self):
        match = self.get_instance(
            Feature, 'web-css-background-size-basic_support')
        self.assert_feature_params_by_name(
            'Basic Support', match, match.id, match.slug)

    def test_feature_params_by_name_match_canonical(self):
        match = self.create(
            Feature, parent=self.parent, name={'zxx': 'list-item'},
            slug='wcb-list-item')
        self.assert_feature_params_by_name(
            'list-item', match, match.id, match.slug)

    def test_feature_params_by_name_slug_collision(self):
        self.create(Feature, slug='web-css-background-size_slug')
        self.assert_feature_params_by_name(
            'slug', None, '_slug', 'web-css-background-size_slug1')


class TestDataSupportIdByRelations(TestDataBase):
    def setUp(self):
        super(TestDataSupportIdByRelations, self).setUp()
        self.version = self.get_instance(Version, ('firefox', 'current'))
        self.feature = self.get_instance(
            Feature, 'web-css-background-size-basic_support')

    def assert_new_support_id(self, version_id, feature_id):
        support_id = self.data.support_id_by_relations(version_id, feature_id)
        expected_support_id = '_{}-{}'.format(feature_id, version_id)
        self.assertEqual(expected_support_id, support_id)

    def test_all_new(self):
        self.assert_new_support_id('_version', '_feature')

    def test_real_version(self):
        self.assert_new_support_id(self.version.id, '_feature')

    def test_real_feature(self):
        self.assert_new_support_id('_version', self.feature.id)

    def test_not_found(self):
        self.assert_new_support_id(self.version.id, self.feature.id)

    def test_found(self):
        support = self.create(
            Support, version=self.version, feature=self.feature)
        support_id = self.data.support_id_by_relations(
            self.version.id, self.feature.id)
        self.assertEqual(support.id, support_id)


class TestDataVersionParamsByVersion(TestDataBase):
    def setUp(self):
        super(TestDataVersionParamsByVersion, self).setUp()
        self.browser = self.get_instance(Browser, 'firefox')

    def test_new_browser(self):
        params = self.data.version_params_by_version(
            '_browser', 'Browser', '1.0')
        self.assertIsNone(params.version)
        self.assertEqual('_Browser-1.0', params.version_id)

    def test_new_version(self):
        params = self.data.version_params_by_version(
            self.browser.id, self.browser.name['en'], '1.0')
        self.assertIsNone(params.version)
        self.assertEqual('_Firefox-1.0', params.version_id)

    def test_existing_version(self):
        version = self.get_instance(Version, ('firefox', 'current'))
        params = self.data.version_params_by_version(
            self.browser.id, self.browser.name['en'], 'current')
        self.assertEqual(version, params.version)
        self.assertEqual(version.id, params.version_id)
