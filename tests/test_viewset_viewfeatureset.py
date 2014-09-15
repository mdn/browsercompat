#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.ViewFeatureSetViewSet` class.
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from .base import APITestCase


class TestViewFeatureSetViewSet(APITestCase):
    def test_get_list(self):
        url = reverse('viewfeaturesets-list')
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

    def test_get_detail(self):
        url = reverse(
            'viewfeaturesets-detail', kwargs={'pk': 'html-element-address'})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)
