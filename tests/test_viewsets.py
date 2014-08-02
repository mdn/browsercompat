#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` viewsets module.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from webplatformcompat.models import Browser


class TestBrowserViewset(APITestCase):

    def test_get(self):
        browser = Browser.objects.create()
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.get(url)
        expected_data = {
            'id': 1,
            'slug': '',
            'icon': '',
            'name': '',
            'note': None}
        self.assertEqual(response.data, expected_data)
