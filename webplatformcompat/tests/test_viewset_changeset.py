#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.ChangesetViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import dumps, loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.history import Changeset
from webplatformcompat.models import Feature

from .base import APITestCase


class TestChangesetViewSet(APITestCase):
    def test_get(self):
        user = self.login_superuser()
        test_date = datetime(2014, 10, 27, 14, 3, 31, 530945, UTC)
        feature = self.create(
            Feature, _history_user=user, _history_date=test_date)
        changeset = feature.history.all()[0].history_changeset
        Changeset.objects.filter(id=changeset.id).update(modified=test_date)
        url = reverse('changeset-detail', kwargs={'pk': changeset.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': changeset.id,
            'created': changeset.created,
            'modified': changeset.created,
            'target_resource_type': None,
            'target_resource_id': None,
            'closed': True,
            'user': user.pk,
            'historical_browsers': [],
            'historical_versions': [],
            "historical_features": [feature.pk],
            'historical_specifications': [],
            'historical_supports': [],
            'historical_maturities': [],
            'historical_sections': [],
        }
        self.assertDataEqual(expected_data, response.data)

        expected_json = {
            "changesets": {
                "id": str(changeset.id),
                "created": "2014-10-27T14:03:31.530Z",
                "modified": "2014-10-27T14:03:31.530Z",
                "closed": True,
                'target_resource_type': None,
                'target_resource_id': None,
                "links": {
                    'user': str(user.pk),
                    'historical_browsers': [],
                    'historical_versions': [],
                    "historical_features": [str(feature.pk)],
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

    def test_simple_changeset(self):
        # A simple changeset is auto-created, auto-closed
        self.login_superuser()
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

    def test_post_empty(self):
        self.login_superuser()
        response = self.client.post(reverse('changeset-list'), {})
        self.assertEqual(201, response.status_code, response.content)
        changeset = Changeset.objects.get()
        expected_data = {
            u'id': 1,
            u'created': changeset.created,
            u'modified': changeset.modified,
            u'closed': False,
            u'target_resource_type': None,
            u'target_resource_id': None,
            u'user': 1,
            u'historical_browsers': [],
            u'historical_features': [],
            u'historical_maturities': [],
            u'historical_sections': [],
            u'historical_specifications': [],
            u'historical_supports': [],
            u'historical_versions': [],
        }
        self.assertDataEqual(response.data, expected_data)
