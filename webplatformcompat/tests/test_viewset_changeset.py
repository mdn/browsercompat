#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.ChangesetViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import dumps, loads
from pytz import UTC
import mock

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from webplatformcompat.history import Changeset
from webplatformcompat.models import Browser, Feature, Support, Version

from .base import APITestCase


class TestChangesetViewSet(APITestCase):
    def setUp(self):
        self.user = self.login_user()

    def test_get(self):
        test_date = datetime(2014, 10, 27, 14, 3, 31, 530945, UTC)
        feature = self.create(
            Feature, _history_user=self.user, _history_date=test_date)
        feature_history = feature.history.all()[0]
        changeset = Changeset.objects.get()
        url = reverse('changeset-detail', kwargs={'pk': changeset.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': changeset.id,
            'created': self.dt_repr(changeset.created),
            'modified': self.dt_repr(changeset.modified),
            'target_resource_type': None,
            'target_resource_id': None,
            'closed': False,
            'user': self.user.pk,
            'historical_browsers': [],
            'historical_versions': [],
            "historical_features": [feature_history.pk],
            'historical_specifications': [],
            'historical_supports': [],
            'historical_maturities': [],
            'historical_sections': [],
        }
        actual_data = response.data.copy()
        self.assertDataEqual(expected_data, actual_data)

        expected_json = {
            "changesets": {
                "id": str(changeset.id),
                "created": self.dt_json(changeset.created),
                "modified": self.dt_json(changeset.modified),
                "closed": False,
                'target_resource_type': None,
                'target_resource_id': None,
                "links": {
                    'user': str(self.user.pk),
                    'historical_browsers': [],
                    'historical_versions': [],
                    "historical_features": [str(feature_history.pk)],
                    'historical_specifications': [],
                    'historical_supports': [],
                    'historical_maturities': [],
                    'historical_sections': [],
                },
            },
            "links": {
                'changesets.user': {
                    'href': (
                        'http://testserver/api/v1/users/'
                        '{changesets.user}'),
                    'type': 'users'
                },
                "changesets.historical_browsers": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_browsers/"
                        "{changesets.historical_browsers}"),
                    "type": "historical_browsers",
                },
                "changesets.historical_versions": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_versions/"
                        "{changesets.historical_versions}"),
                    "type": "historical_versions",
                },
                "changesets.historical_features": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_features/"
                        "{changesets.historical_features}"),
                    "type": "historical_features",
                },
                "changesets.historical_supports": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_supports/"
                        "{changesets.historical_supports}"),
                    "type": "historical_supports",
                },
                "changesets.historical_specifications": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_specifications/"
                        "{changesets.historical_specifications}"),
                    "type": "historical_specifications",
                },
                "changesets.historical_maturities": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_maturities/"
                        "{changesets.historical_maturities}"),
                    "type": "historical_maturities",
                },
                "changesets.historical_sections": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_sections/"
                        "{changesets.historical_sections}"),
                    "type": "historical_sections",
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    @mock.patch('webplatformcompat.tasks.update_cache_for_instance')
    def test_simple_changeset(self, mock_task):
        # A simple changeset is auto-created, auto-closed, cache refreshed
        data = {
            'features': {
                'slug': 'feature',
                'name': {'en': 'The Feature'}
            }
        }
        response = self.client.post(
            reverse('feature-list'), dumps(data),
            content_type='application/vnd.api+json')
        self.assertEqual(201, response.status_code, response.content)
        feature = Feature.objects.get()
        changeset = feature.history.all()[0].history_changeset
        self.assertTrue(changeset.closed)
        mock_task.assertCalledOnce('Feature', feature.id)

    @mock.patch('webplatformcompat.tasks.update_cache_for_instance')
    def test_multiple_changeset(self, mock_task):
        # A multiple changeset is manually created, and must be marked complete
        # Cache updated are delayed until end

        mock_task.reset_mock()
        mock_task.side_effect = Exception('Not called')
        mock_task.delay.side_effect = Exception('Not called')

        # Open a changeset
        japi = 'application/vnd.api+json'
        response = self.client.post(
            reverse('changeset-list'), dumps({}), content_type=japi)
        self.assertEqual(201, response.status_code, response.content)
        changeset = Changeset.objects.get()
        c = '?changeset=%s' % changeset.id

        # Add some new resources to the changeset
        data = {
            'browsers': {
                'slug': 'browser',
                'name': {'en': 'The Browser'},
            }}
        response = self.client.post(
            reverse('browser-list') + c, dumps(data), content_type=japi)
        self.assertEqual(201, response.status_code, response.content)
        browser = Browser.objects.get()

        data = {
            'versions': {
                'links': {
                    'browser': browser.id
                }}}
        response = self.client.post(
            reverse('version-list') + c, dumps(data), content_type=japi)
        self.assertEqual(201, response.status_code, response.content)
        version = Version.objects.get()

        data = {
            'features': {
                'slug': 'feature',
                'name': {'en': 'The Feature'}
            }}
        response = self.client.post(
            reverse('feature-list') + c, dumps(data), content_type=japi)
        self.assertEqual(201, response.status_code, response.content)
        feature = Feature.objects.get()

        data = {
            'supports': {
                'links': {
                    'version': version.id,
                    'feature': feature.id,
                }}}
        response = self.client.post(
            reverse('support-list') + c, dumps(data), content_type=japi)
        self.assertEqual(201, response.status_code, response.content)
        support = Support.objects.get()

        # Resource history is associated with the changeset
        url = reverse('changeset-detail', kwargs={'pk': changeset.id})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, response.content)
        changeset = Changeset.objects.get()
        expected_data = {
            u'id': changeset.id,
            u'created': self.dt_repr(changeset.created),
            u'modified': self.dt_repr(changeset.modified),
            u'closed': False,
            u'target_resource_type': None,
            u'target_resource_id': None,
            u'user': self.user.id,
            u'historical_browsers': [browser.history.all()[0].pk],
            u'historical_features': [feature.history.all()[0].pk],
            u'historical_maturities': [],
            u'historical_sections': [],
            u'historical_specifications': [],
            u'historical_supports': [support.history.all()[0].pk],
            u'historical_versions': [version.history.all()[0].pk],
        }
        self.assertDataEqual(response.data, expected_data)

        # Close the changeset
        mock_task.delay.side_effect = None
        data = {
            'changesets': {
                'closed': True
            }}
        response = self.client.put(url, dumps(data), content_type=japi)
        self.assertEqual(200, response.status_code, response.content)
        changeset = Changeset.objects.get()
        expected_data['modified'] = self.dt_repr(changeset.modified)
        expected_data['closed'] = True
        self.assertDataEqual(response.data, expected_data)
        expected_calls = [
            mock.call('Browser', browser.pk),
            mock.call('Feature', feature.pk),
            mock.call('Version', version.pk),
            mock.call('Support', support.pk),
        ]
        self.assertEqual(4, mock_task.delay.call_count)
        mock_task.delay.assert_has_calls(expected_calls, any_order=True)

    def test_cannot_use_closed_changeset_json_api(self):
        changeset = Changeset.objects.create(user=self.user, closed=True)

        data = {
            'browsers': {
                'slug': 'browser',
                'name': {'en': 'The Browser'},
            }}
        response = self.client.post(
            reverse('browser-list') + '?changeset=%s' % changeset.id,
            dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(400, response.status_code, response.content)
        expected_content = {
            'errors': {
                'changeset': 'Changeset %d is closed.' % changeset.id,
            }
        }
        self.assertEqual(
            loads(response.content.decode('utf-8')), expected_content)

    def test_cannot_use_closed_changeset_regular_request(self):
        changeset = Changeset.objects.create(user=self.user, closed=True)

        data = {
            'slug': 'browser',
            'name': {'en': 'The Browser'},
        }
        response = self.client.post(
            reverse('browser-list') + '?changeset=%s' % changeset.id, data)
        self.assertEqual(400, response.status_code, response.content)
        message = 'Changeset %d is closed.' % changeset.id
        self.assertEqual(response.content.decode('utf-8'), message)

    def test_user_mismatch(self):
        other = User.objects.create(username='other')
        changeset = Changeset.objects.create(user=other)

        data = {
            'slug': 'browser',
            'name': {'en': 'The Browser'},
        }
        response = self.client.post(
            reverse('browser-list') + '?changeset=%s' % changeset.id, data)
        self.assertEqual(400, response.status_code, response.content)
        message = 'Changeset %d has a different user.' % changeset.id
        self.assertEqual(response.content.decode('utf-8'), message)

    def test_post_empty(self):
        response = self.client.post(reverse('changeset-list'), {})
        self.assertEqual(201, response.status_code, response.content)
        changeset = Changeset.objects.get()
        expected_data = {
            u'id': changeset.id,
            u'created': self.dt_repr(changeset.created),
            u'modified': self.dt_repr(changeset.modified),
            u'closed': False,
            u'target_resource_type': None,
            u'target_resource_id': None,
            u'user': self.user.id,
            u'historical_browsers': [],
            u'historical_features': [],
            u'historical_maturities': [],
            u'historical_sections': [],
            u'historical_specifications': [],
            u'historical_supports': [],
            u'historical_versions': [],
        }
        self.assertDataEqual(response.data, expected_data)
