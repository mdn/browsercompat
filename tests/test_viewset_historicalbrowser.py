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

    def fix_data(self, data):
        '''Fix response.data dictionary'''
        out = dict(data)
        out['browsers'] = dict(out['browsers'])
        out['browsers']['name'] = dict(out['browsers']['name'])
        return out

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
        self.assertDictEqual(expected_data, self.fix_data(response.data))
        expected_json = {
            'historical_browsers': {
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
                'historical_browsers.browser': {
                    'href': (
                        'http://testserver/api/browsers/'
                        '{historical_browsers.browser}'),
                    'type': 'browsers'
                },
                'historical_browsers.user': {
                    'href': (
                        'http://testserver/api/users/'
                        '{historical_browsers.user}'),
                    'type': 'users'
                }
            }
        }
        self.assertDictEqual(
            expected_json, loads(response.content.decode('utf-8')))

    def test_filter_by_id(self):
        user = self.login_superuser()
        self.create(
            Browser, slug='other', name={'en': 'Other Browser'})
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'},
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 17, 58, 26, 915222, UTC))
        bh = browser.history.all()[0]
        url = reverse('historicalbrowser-list')
        response = self.client.get(url, {'id': browser.id})
        expected_data = {
            'id': bh.history_id,
            'date': browser._history_date,
            'event': 'created',
            'user': self.reverse('user-detail', pk=user.pk),
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'browsers': {
                'id': str(browser.pk),
                'slug': 'browser',
                'icon': None,
                'name': {'en': 'A Browser'},
                'note': None,
                'links': {'history_current': str(bh.pk)}
            },
        }
        self.assertEqual(1, len(response.data))
        self.assertEqual(expected_data, self.fix_data(response.data[0]))

    def test_filter_by_slug(self):
        user = self.login_superuser()
        self.create(
            Browser, slug='other', name={'en': 'Other Browser'})
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'},
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 17, 58, 26, 915222, UTC))
        bh = browser.history.all()[0]
        url = reverse('historicalbrowser-list')
        response = self.client.get(url, {'slug': 'browser'})
        expected_data = {
            'id': bh.history_id,
            'date': browser._history_date,
            'event': 'created',
            'user': self.reverse('user-detail', pk=user.pk),
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'browsers': {
                'id': str(browser.pk),
                'slug': 'browser',
                'icon': None,
                'name': {'en': 'A Browser'},
                'note': None,
                'links': {'history_current': str(bh.pk)}
            },
        }
        self.assertEqual(1, len(response.data))
        self.assertEqual(expected_data, self.fix_data(response.data[0]))
