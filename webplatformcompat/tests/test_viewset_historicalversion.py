#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.HistoricalVersionViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, Version

from .base import APITestCase


class TestHistoricalVersionViewset(APITestCase):

    def test_get(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        version = self.create(
            Version, browser=browser, version="1.0",
            _history_user=self.user,
            _history_date=datetime(2014, 9, 4, 19, 13, 25, 857510, UTC))
        history = version.history.all()[0]
        url = reverse('historicalversion-detail', kwargs={'pk': history.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': history.pk,
            'date': self.dt_repr(version._history_date),
            'event': 'created',
            'changeset': history.history_changeset_id,
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
                    'browser': str(browser.id),
                    'history_current': str(history.pk),
                }
            },
        }
        self.assertDataEqual(expected_data, response.data)
        expected_json = {
            'historical_versions': {
                'id': str(history.pk),
                'date': self.dt_json(version._history_date),
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
                        'browser': str(browser.id),
                        'history_current': str(history.pk),
                    },
                },
                'links': {
                    'version': str(version.pk),
                    'changeset': str(history.history_changeset_id),
                },
            },
            'links': {
                'historical_versions.version': {
                    'href': (
                        'http://testserver/api/v1/versions/'
                        '{historical_versions.version}'),
                    'type': 'versions'
                },
                'historical_versions.changeset': {
                    'href': (
                        'http://testserver/api/v1/changesets/'
                        '{historical_versions.changeset}'),
                    'type': 'changesets'
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_id(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        self.create(Version, browser=browser, version="1.0")
        version = self.create(
            Version, browser=browser, version="2.0",
            _history_user=self.user,
            _history_date=datetime(2014, 9, 4, 20, 46, 28, 479175, UTC))
        history = version.history.all()[0]
        url = reverse('historicalversion-list')
        response = self.client.get(url, {'id': version.id})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': self.dt_repr(version._history_date),
                'event': 'created',
                'changeset': history.history_changeset_id,
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
                        'browser': str(browser.id),
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)
