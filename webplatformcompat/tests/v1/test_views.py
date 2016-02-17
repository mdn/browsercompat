# -*- coding: utf-8 -*-
"""Tests for v1 API views."""

from json import loads

from .base import TestCase


class TestViews(TestCase):
    def full_api_reverse(self, viewname):
        """Create a full URL for a namespaced API view."""
        return 'http://testserver' + self.api_reverse(viewname)

    def test_api_root(self):
        response = self.client.get(self.api_reverse('api-root'))
        expected = {
            'resources': {
                'browsers': self.full_api_reverse('browser-list'),
                'features': self.full_api_reverse('feature-list'),
                'maturities': self.full_api_reverse('maturity-list'),
                'references': self.full_api_reverse('reference-list'),
                'specifications': self.full_api_reverse('specification-list'),
                'sections': self.full_api_reverse('section-list'),
                'supports': self.full_api_reverse('support-list'),
                'versions': self.full_api_reverse('version-list'),
            },
            'change_control': {
                'changesets': self.full_api_reverse('changeset-list'),
                'users': self.full_api_reverse('user-list'),
            },
            'history': {
                'historical_browsers': self.full_api_reverse(
                    'historicalbrowser-list'),
                'historical_features': self.full_api_reverse(
                    'historicalfeature-list'),
                'historical_maturities': self.full_api_reverse(
                    'historicalmaturity-list'),
                'historical_references': self.full_api_reverse(
                    'historicalreference-list'),
                'historical_sections': self.full_api_reverse(
                    'historicalsection-list'),
                'historical_specifications': self.full_api_reverse(
                    'historicalspecification-list'),
                'historical_supports': self.full_api_reverse(
                    'historicalsupport-list'),
                'historical_versions': self.full_api_reverse(
                    'historicalversion-list'),
            },
            'views': {
                'view_features': self.full_api_reverse('viewfeatures-list')
            },
        }
        actual = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected, actual)
