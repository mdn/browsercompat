# -*- coding: utf-8 -*-
"""Tests for the API views."""

from django.core.urlresolvers import reverse

from .base import TestCase


class TestViews(TestCase):
    def test_home(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_feature(self):
        response = self.client.get(
            reverse('view_feature', kwargs={'feature_id': 1}))
        self.assertEqual(response.status_code, 200)

    def test_browse_app(self):
        response = self.client.get(reverse('browse'))
        self.assertEqual(response.status_code, 200)
