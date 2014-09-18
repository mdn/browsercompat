#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.HistoricalVersionViewSet` class.
"""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, Version

from .base import APITestCase


class TestHistoricalVersionViewset(APITestCase):

    def test_get(self):
        user = self.login_superuser()
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        version = self.create(
            Version, browser=browser, version="1.0",
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 19, 13, 25, 857510, UTC))
        vh = version.history.all()[0]
        url = reverse('historicalversion-detail', kwargs={'pk': vh.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': vh.history_id,
            'date': version._history_date,
            'event': 'created',
            'user': user.pk,
            'version': version.pk,
            'versions': {
                'id': str(version.id),
                'version': '1.0',
                'release_day': None,
                'retirement_day': None,
                'status': 'unknown',
                'release_notes_uri': None,
                'note': None,
                'order': 0,
                'links': {
                    'history_current': str(vh.id),
                }
            },
        }
        self.assertDataEqual(expected_data, response.data)
        expected_json = {
            'historical_versions': {
                'id': str(vh.history_id),
                'date': '2014-09-04T19:13:25.857Z',
                'event': 'created',
                'versions': {
                    'id': str(version.id),
                    'version': '1.0',
                    'release_day': None,
                    'retirement_day': None,
                    'status': 'unknown',
                    'release_notes_uri': None,
                    'note': None,
                    'order': 0,
                    'links': {
                        'history_current': str(vh.id),
                    },
                },
                'links': {
                    'version': str(version.pk),
                    'user': str(user.pk),
                },
            },
            'links': {
                'historical_versions.version': {
                    'href': (
                        'http://testserver/api/v1/versions/'
                        '{historical_versions.version}'),
                    'type': 'versions'
                },
                'historical_versions.user': {
                    'href': (
                        'http://testserver/api/v1/users/'
                        '{historical_versions.user}'),
                    'type': 'users'
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_id(self):
        user = self.login_superuser()
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        self.create(Version, browser=browser, version="1.0")
        version = self.create(
            Version, browser=browser, version="2.0",
            _history_user=user,
            _history_date=datetime(2014, 9, 4, 20, 46, 28, 479175, UTC))
        vh = version.history.all()[0]
        url = reverse('historicalversion-list')
        response = self.client.get(url, {'id': version.id})
        expected_data = [{
            'id': vh.history_id,
            'date': version._history_date,
            'event': 'created',
            'user': user.pk,
            'version': version.pk,
            'versions': {
                'id': str(version.pk),
                'version': '2.0',
                'release_day': None,
                'retirement_day': None,
                'status': 'unknown',
                'release_notes_uri': None,
                'note': None,
                'order': 1,
                'links': {
                    'history_current': str(vh.id),
                }
            },
        }]
        self.assertDataEqual(expected_data, response.data)
