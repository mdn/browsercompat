#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.HistoricalBrowserViewSet` class.
"""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser

from .base import APITestCase


class TestHistoricalBrowserViewset(APITestCase):
    def test_get(self):
        user = self.login_superuser()
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'},
            _history_user=user,
            _history_date=datetime(2014, 8, 25, 20, 50, 38, 868903, UTC))
        bh = browser.history.all()[0]
        url = reverse('historicalbrowser-detail', kwargs={'pk': bh.pk})
        response = self.client.get(
            url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': bh.history_id,
            'date': browser._history_date,
            'event': 'created',
            'user': self.reverse('user-detail', pk=user.pk),
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'browsers': {
                'id': '1',
                'slug': 'browser',
                'icon': None,
                'name': {'en': 'A Browser'},
                'note': None,
                'links': {'history_current': '1'}
            },
        }
        actual = dict(response.data)
        actual['browsers'] = dict(actual['browsers'])
        actual['browsers']['name'] = dict(actual['browsers']['name'])
        self.assertDictEqual(expected_data, actual)
        expected_json = {
            'historical-browsers': {
                'id': '1',
                'date': '2014-08-25T20:50:38.868Z',
                'event': 'created',
                'browsers': {
                    'id': '1',
                    'slug': 'browser',
                    'icon': None,
                    'name': {
                        'en': 'A Browser'
                    },
                    'note': None,
                    'links': {
                        'history_current': '1'
                    },
                },
                'links': {
                    'browser': str(browser.pk),
                    'user': str(user.pk),
                }
            },
            'links': {
                'historical-browsers.browser': {
                    'href': (
                        'http://testserver/api/browsers/'
                        '{historical-browsers.browser}'),
                    'type': 'browsers'
                },
                'historical-browsers.user': {
                    'href': (
                        'http://testserver/api/users/'
                        '{historical-browsers.user}'),
                    'type': 'users'
                }
            }
        }
        self.assertDictEqual(
            expected_json, loads(response.content.decode('utf-8')))
