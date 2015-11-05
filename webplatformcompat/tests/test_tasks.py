#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webplatformcompat/tasks.py."""
from django.test.utils import override_settings
import mock

from webplatformcompat.models import Maturity, Specification
from webplatformcompat.tasks import update_cache_for_instance

from .base import TestCase


class TestUpdateCacheForInstance(TestCase):
    def setUp(self):
        self.mat = self.create(Maturity, slug='maturity')
        self.spec = self.create(Specification, maturity=self.mat)
        self.patcher = mock.patch('webplatformcompat.tasks.Cache')
        self.mock_cache = mock.Mock(spec_set=['update_instance'])
        self.mock_cache_class = self.patcher.start()
        self.mock_cache_class.return_value = self.mock_cache

    def tearDown(self):
        self.patcher.stop()

    def test_update_cache_no_invalidation(self):
        self.mock_cache.update_instance.return_value = []
        update_cache_for_instance('Maturity', self.mat.id)
        self.mock_cache.update_instance.assert_called_once_with(
            'Maturity', self.mat.id, None, None, update_only=False)

    @override_settings(DRF_INSTANCE_CACHE_POPULATE_COLD=True)
    def test_update_cache_with_invalidation(self):
        results = [
            [('Maturity', self.mat.id, 'v1')],
            [],
        ]

        def side_effect(*args, **kwargs):
            return results.pop(0)

        self.mock_cache.update_instance.side_effect = side_effect
        update_cache_for_instance('Specification', self.spec.id)
        expected_calls = [
            mock.call(
                'Specification', self.spec.id, None, None, update_only=False),
            mock.call('Maturity', self.mat.id, None, 'v1', update_only=False)]
        actual_calls = self.mock_cache.update_instance.call_args_list
        self.assertEqual(expected_calls, actual_calls)
