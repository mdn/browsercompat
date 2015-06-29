# coding: utf-8
"""Test mdn.data"""
from __future__ import unicode_literals

from mdn.data import Data
from webplatformcompat.models import Feature, Specification
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
