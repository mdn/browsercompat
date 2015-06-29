# coding: utf-8
"""Test mdn.data"""
from __future__ import unicode_literals

from mdn.data import Data
from webplatformcompat.models import Specification
from .base import TestCase


class TestData(TestCase):
    def setUp(self):
        self.data = Data()

    def test_specification_by_key_missing(self):
        with self.assertNumQueries(1):
            self.assertIsNone(self.data.specification_by_key("NoSpec"))
        with self.assertNumQueries(0):
            self.assertIsNone(self.data.specification_by_key("NoSpec"))

    def test_specification_by_key_found(self):
        spec = self.get_instance(Specification, 'css3_backgrounds')
        key = spec.mdn_key
        with self.assertNumQueries(1):
            self.assertEqual(spec, self.data.specification_by_key(key))
        with self.assertNumQueries(0):
            self.assertEqual(spec, self.data.specification_by_key(key))
