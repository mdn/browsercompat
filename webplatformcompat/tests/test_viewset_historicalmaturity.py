#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.HistoricalMaturityViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Maturity

from .base import APITestCase


class TestHistoricalMaturityViewset(APITestCase):
    def setUp(self):
        self.user = self.login_user()

    def test_get(self):
        maturity = self.create(
            Maturity, slug="CR", name={"en": "Candidate Recommendation"},
            _history_user=self.user,
            _history_date=datetime(2014, 10, 19, 10, 20, 45, 609995, UTC))
        history = maturity.history.all()[0]
        url = reverse('historicalmaturity-detail', kwargs={'pk': history.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': history.pk,
            'date': maturity._history_date,
            'event': 'created',
            'changeset': history.history_changeset_id,
            'maturity': maturity.pk,
            'maturities': {
                'id': str(maturity.id),
                'slug': 'CR',
                'name': {'en': 'Candidate Recommendation'},
                'links': {
                    'history_current': str(history.pk),
                }
            },
        }
        self.assertDataEqual(expected_data, response.data)
        expected_json = {
            'historical_maturities': {
                'id': str(history.pk),
                'date': '2014-10-19T10:20:45.609Z',
                'event': 'created',
                'maturities': {
                    'id': str(maturity.id),
                    'slug': 'CR',
                    'name': {'en': 'Candidate Recommendation'},
                    'links': {
                        'history_current': str(history.pk),
                    }
                },
                'links': {
                    'maturity': str(maturity.pk),
                    'changeset': str(history.history_changeset_id),
                },
            },
            'links': {
                'historical_maturities.maturity': {
                    'href': (
                        'http://testserver/api/v1/maturities/'
                        '{historical_maturities.maturity}'),
                    'type': 'maturities'
                },
                'historical_maturities.changeset': {
                    'href': (
                        'http://testserver/api/v1/changesets/'
                        '{historical_maturities.changeset}'),
                    'type': 'changesets'
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_id(self):
        maturity = self.create(
            Maturity, slug="PR", name={'en-US': 'Proposed Recommendation'},
            _history_user=self.user,
            _history_date=datetime(2014, 10, 19, 10, 23, 38, 279164, UTC))
        history = maturity.history.all()[0]
        url = reverse('historicalmaturity-list')
        response = self.client.get(url, {'id': maturity.id})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': maturity._history_date,
                'event': 'created',
                'changeset': history.history_changeset_id,
                'maturity': maturity.pk,
                'maturities': {
                    'id': str(maturity.pk),
                    'slug': 'PR',
                    'name': {'en-US': 'Proposed Recommendation'},
                    'links': {
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)
