#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.HistoricalBrowserVersionViewSet` class.
"""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, BrowserVersion

from .base import APITestCase


class TestHistoricalBrowserVersionViewset(APITestCase):

    def fix_data(self, data):
        '''Fix response.data dictionary'''
        out = dict(data)
        out['browser_versions'] = dict(out['browser_versions'])
        return out

    def test_get(self):
        user = self.login_superuser()
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        bversion = self.create(
            BrowserVersion, browser=browser, version="1.0",
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 19, 13, 25, 857510, UTC))
        bvh = bversion.history.all()[0]
        url = reverse('historicalbrowserversion-detail', kwargs={'pk': bvh.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': bvh.history_id,
            'date': bversion._history_date,
            'event': 'created',
            'user': self.reverse('user-detail', pk=user.pk),
            'browser_version': self.reverse(
                'browserversion-detail', pk=bversion.pk),
            'browser_versions': {
                'id': str(bversion.id),
                'version': '1.0',
                'release_day': None,
                'retirement_day': None,
                'status': 'unknown',
                'release_notes_uri': None,
                'note': None,
                'order': 0,
                'links': {
                    'history_current': str(bvh.id),
                }
            },
        }
        self.assertDictEqual(expected_data, self.fix_data(response.data))
        expected_json = {
            'historical-browser-versions': {
                'id': str(bvh.history_id),
                'date': '2014-09-04T19:13:25.857Z',
                'event': 'created',
                'browser_versions': {
                    'id': str(bversion.id),
                    'version': '1.0',
                    'release_day': None,
                    'retirement_day': None,
                    'status': 'unknown',
                    'release_notes_uri': None,
                    'note': None,
                    'order': 0,
                    'links': {
                        'history_current': str(bvh.id),
                    },
                },
                'links': {
                    'browser_version': str(bversion.pk),
                    'user': str(user.pk),
                },
            },
            'links': {
                'historical-browser-versions.browser_version': {
                    'href': (
                        'http://testserver/api/browser-versions/'
                        '{historical-browser-versions.browser_version}'),
                    'type': 'browser-versions'
                },
                'historical-browser-versions.user': {
                    'href': (
                        'http://testserver/api/users/'
                        '{historical-browser-versions.user}'),
                    'type': 'users'
                },
            }
        }
        self.assertDictEqual(
            expected_json, loads(response.content.decode('utf-8')))

    def test_filter_by_id(self):
        user = self.login_superuser()
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        self.create(BrowserVersion, browser=browser, version="1.0")
        bversion = self.create(
            BrowserVersion, browser=browser, version="2.0",
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 20, 46, 28, 479175, UTC))
        bvh = bversion.history.all()[0]
        url = reverse('historicalbrowserversion-list')
        response = self.client.get(url, {'id': bversion.id})
        expected_data = {
            'id': bvh.history_id,
            'date': bversion._history_date,
            'event': 'created',
            'user': self.reverse('user-detail', pk=user.pk),
            'browser_version': self.reverse(
                'browserversion-detail', pk=bversion.pk),
            'browser_versions': {
                'id': str(bversion.pk),
                'version': '2.0',
                'release_day': None,
                'retirement_day': None,
                'status': 'unknown',
                'release_notes_uri': None,
                'note': None,
                'order': 1,
                'links': {
                    'history_current': str(bvh.id),
                }
            },
        }
        self.assertEqual(1, len(response.data))
        self.assertEqual(expected_data, self.fix_data(response.data[0]))
