# -*- coding: utf-8 -*-
"""Tests for view serializers under v1 API."""

from webplatformcompat.view_serializers import DjangoResourceClient
from webplatformcompat.history import Changeset

from ..test_view_serializers import (
    TestBaseViewFeatureViewSet, TestBaseViewFeatureUpdates)
from .base import TestCase


class TestViewFeatureViewSet(TestBaseViewFeatureViewSet):
    namespace = 'v1'
    __test__ = True


class TestViewFeatureUpdates(TestBaseViewFeatureUpdates):
    namespace = 'v1'
    __test__ = True


class TestDjangoResourceClient(TestCase):
    def setUp(self):
        self.client = DjangoResourceClient()

    def test_url_maturity_list(self):
        expected = self.api_reverse('maturity-list')
        self.assertEqual(expected, self.client.url('maturities'))

    def test_url_feature_detail(self):
        expected = self.api_reverse('feature-detail', pk='55')
        self.assertEqual(expected, self.client.url('features', '55'))

    def test_open_changeset(self):
        self.client.open_changeset()
        self.assertFalse(Changeset.objects.exists())

    def test_close_changeset(self):
        self.client.close_changeset()
        self.assertFalse(Changeset.objects.exists())

    def test_delete(self):
        self.assertRaises(
            NotImplementedError, self.client.delete, 'features', '666')
