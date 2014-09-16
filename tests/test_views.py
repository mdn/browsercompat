#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` views module.
"""
from json import loads

from django.core.urlresolvers import reverse
from django.test import TestCase


class TestViews(TestCase):
    maxDiff = None

    def reverse(self, viewname, **kwargs):
        return 'http://testserver' + reverse(viewname, kwargs=kwargs)

    def test_home(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_api_root(self):
        response = self.client.get(reverse('api-root'))
        expected = {
            'resources': {
                'browsers': self.reverse('browser-list'),
                'versions': self.reverse('version-list'),
            },
            'change-control': {
                'users': self.reverse('user-list'),
            },
            'history': {
                'historical-browsers': self.reverse('historicalbrowser-list'),
                'historical-versions':
                    self.reverse('historicalversion-list'),
            },
            'views': {
                'views/features': self.reverse('viewfeatures-list')
            },
        }
        self.assertEqual(expected, loads(response.content.decode('utf-8')))
