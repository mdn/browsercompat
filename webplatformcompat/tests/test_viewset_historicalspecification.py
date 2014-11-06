#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for HistoricalSpecificationViewSet class."""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.core.urlresolvers import reverse

from webplatformcompat.models import Maturity, Specification

from .base import APITestCase


class TestHistoricalSpecificationViewset(APITestCase):

    def test_get(self):
        user = self.login_superuser()
        maturity = self.create(
            Maturity, slug='M', name={'en': 'A Maturity'})
        spec = self.create(
            Specification, maturity=maturity, slug="spec",
            name={'en': 'A Specification'},
            uri={'en': 'http://example.com/spec.html'},
            _history_user=user,
            _history_date=datetime(2014, 10, 19, 11, 46, 10, 834522, UTC))
        history = spec.history.all()[0]
        url = reverse(
            'historicalspecification-detail', kwargs={'pk': history.pk})
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': history.pk,
            'date': spec._history_date,
            'event': 'created',
            'changeset': history.history_changeset_id,
            'specification': spec.pk,
            'specifications': {
                'id': str(spec.id),
                'slug': 'spec',
                'mdn_key': None,
                'name': {'en': 'A Specification'},
                'uri': {'en': 'http://example.com/spec.html'},
                'links': {
                    'maturity': str(maturity.id),
                    'history_current': str(history.pk),
                }
            },
        }
        self.assertDataEqual(expected_data, response.data)
        expected_json = {
            'historical_specifications': {
                'id': str(history.pk),
                'date': '2014-10-19T11:46:10.834Z',
                'event': 'created',
                'specifications': {
                    'id': str(spec.id),
                    'slug': 'spec',
                    'mdn_key': None,
                    'name': {'en': 'A Specification'},
                    'uri': {'en': 'http://example.com/spec.html'},
                    'links': {
                        'maturity': str(maturity.id),
                        'history_current': str(history.pk),
                    },
                },
                'links': {
                    'specification': str(spec.pk),
                    'changeset': str(history.history_changeset_id),
                },
            },
            'links': {
                'historical_specifications.specification': {
                    'href': (
                        'http://testserver/api/v1/specifications/'
                        '{historical_specifications.specification}'),
                    'type': 'specifications'
                },
                'historical_specifications.changeset': {
                    'href': (
                        'http://testserver/api/v1/changesets/'
                        '{historical_specifications.changeset}'),
                    'type': 'changesets'
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_id(self):
        user = self.login_superuser()
        maturity = self.create(
            Maturity, slug='M', name={'en': 'A Maturity'})
        self.create(
            Specification, maturity=maturity, slug='other_spec',
            name={'en': 'Other Spec'}, uri={'en': 'http://w3c.org/spec'})
        spec = self.create(
            Specification, maturity=maturity, slug="spec",
            name={'en': 'A Specification'},
            uri={'en': 'http://example.com/spec.html'},
            _history_user=user,
            _history_date=datetime(2014, 10, 19, 11, 47, 22, 595634, UTC))
        history = spec.history.all()[0]
        url = reverse('historicalspecification-list')
        response = self.client.get(url, {'id': spec.id})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': spec._history_date,
                'event': 'created',
                'changeset': history.history_changeset_id,
                'specification': spec.pk,
                'specifications': {
                    'id': str(spec.pk),
                    'slug': 'spec',
                    'mdn_key': None,
                    'name': {'en': 'A Specification'},
                    'uri': {'en': 'http://example.com/spec.html'},
                    'links': {
                        'maturity': str(maturity.id),
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)

    def test_filter_by_slug(self):
        user = self.login_superuser()
        maturity = self.create(
            Maturity, slug='M', name={'en': 'A Maturity'})
        self.create(
            Specification, maturity=maturity, slug='other_spec',
            name={'en': 'Other Spec'}, uri={'en': 'http://w3c.org/spec'})
        spec = self.create(
            Specification, maturity=maturity, slug="spec",
            name={'en': 'A Specification'},
            uri={'en': 'http://example.com/spec.html'},
            _history_user=user,
            _history_date=datetime(2014, 10, 19, 11, 47, 22, 595634, UTC))
        history = spec.history.all()[0]
        url = reverse('historicalspecification-list')
        response = self.client.get(url, {'slug': 'spec'})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': spec._history_date,
                'event': 'created',
                'changeset': history.history_changeset_id,
                'specification': spec.pk,
                'specifications': {
                    'id': str(spec.pk),
                    'slug': 'spec',
                    'mdn_key': None,
                    'name': {'en': 'A Specification'},
                    'uri': {'en': 'http://example.com/spec.html'},
                    'links': {
                        'maturity': str(maturity.id),
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)

    def test_filter_by_mdn_key(self):
        user = self.login_superuser()
        maturity = self.create(
            Maturity, slug='M', name={'en': 'A Maturity'})
        self.create(
            Specification, maturity=maturity, slug='other_spec',
            name={'en': 'Other Spec'}, uri={'en': 'http://w3c.org/spec'})
        spec = self.create(
            Specification, maturity=maturity, slug="spec", mdn_key="Spec",
            name={'en': 'A Specification'},
            uri={'en': 'http://example.com/spec.html'},
            _history_user=user,
            _history_date=datetime(2014, 10, 19, 11, 47, 22, 595634, UTC))
        history = spec.history.all()[0]
        url = reverse('historicalspecification-list')
        response = self.client.get(url, {'mdn_key': 'Spec'})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': history.pk,
                'date': spec._history_date,
                'event': 'created',
                'changeset': history.history_changeset_id,
                'specification': spec.pk,
                'specifications': {
                    'id': str(spec.pk),
                    'slug': 'spec',
                    'mdn_key': 'Spec',
                    'name': {'en': 'A Specification'},
                    'uri': {'en': 'http://example.com/spec.html'},
                    'links': {
                        'maturity': str(maturity.id),
                        'history_current': str(history.pk),
                    }
                },
            }]}
        self.assertDataEqual(expected_data, response.data)
