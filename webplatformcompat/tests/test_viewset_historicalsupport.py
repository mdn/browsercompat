#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.HistoricalFeatureViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, Feature, Support, Version

from .base import APITestCase


class TestHistoricalSupportViewset(APITestCase):

    def test_get(self):
        user = self.login_superuser()
        browser = self.create(Browser)
        version = self.create(Version, browser=browser)
        feature = self.create(Feature)
        support = self.create(
            Support, version=version, feature=feature,
            _history_user=user,
            _history_date=datetime(2014, 10, 7, 13, 59, 46, 86327, UTC))
        history = support.history.all()[0]
        url = reverse('historicalsupport-detail', kwargs={'pk': history.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': history.pk,
            'date': support._history_date,
            'event': 'created',
            'changeset': history.history_changeset_id,
            'support': support.pk,
            'supports': {
                'id': str(support.id),
                'support': 'yes',
                'prefix': None,
                'prefix_mandatory': False,
                'alternate_name': None,
                'alternate_mandatory': False,
                'requires_config': None,
                'default_config': None,
                'protected': False,
                'note': None,
                'footnote': None,
                'links': {
                    'feature': str(feature.id),
                    'version': str(version.id),
                    'history_current': str(history.pk),
                }
            },
        }
        self.assertDataEqual(expected_data, response.data)
        expected_json = {
            'historical_supports': {
                'id': str(history.pk),
                'date': '2014-10-07T13:59:46.086Z',
                'event': 'created',
                'supports': {
                    'id': str(support.id),
                    'support': 'yes',
                    'prefix': None,
                    'prefix_mandatory': False,
                    'alternate_name': None,
                    'alternate_mandatory': False,
                    'requires_config': None,
                    'default_config': None,
                    'protected': False,
                    'note': None,
                    'footnote': None,
                    'links': {
                        'feature': str(feature.id),
                        'version': str(version.id),
                        'history_current': str(history.pk),
                    }
                },
                'links': {
                    'support': str(support.pk),
                    'changeset': str(history.history_changeset_id),
                },
            },
            'links': {
                'historical_supports.support': {
                    'href': (
                        'http://testserver/api/v1/supports/'
                        '{historical_supports.support}'),
                    'type': 'supports'
                },
                'historical_supports.changeset': {
                    'href': (
                        'http://testserver/api/v1/changesets/'
                        '{historical_supports.changeset}'),
                    'type': 'changesets'
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_id(self):
        user = self.login_superuser()
        browser = self.create(Browser)
        version = self.create(Version, browser=browser)
        feature = self.create(Feature)
        support = self.create(
            Support, version=version, feature=feature,
            _history_user=user,
            _history_date=datetime(2014, 10, 7, 14, 5, 43, 94339, UTC))
        history = support.history.all()[0]
        url = reverse('historicalsupport-list')
        response = self.client.get(url, {'id': support.id})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': support._history_date,
                'event': 'created',
                'changeset': history.history_changeset_id,
                'support': support.pk,
                'supports': {
                    'id': str(support.pk),
                    'support': 'yes',
                    'prefix': None,
                    'prefix_mandatory': False,
                    'alternate_name': None,
                    'alternate_mandatory': False,
                    'requires_config': None,
                    'default_config': None,
                    'protected': False,
                    'note': None,
                    'footnote': None,
                    'links': {
                        'feature': str(feature.id),
                        'version': str(version.id),
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)
