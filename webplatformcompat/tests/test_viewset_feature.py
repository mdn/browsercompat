#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.FeatureViewSet` class.
"""
from __future__ import unicode_literals
from json import loads

from django.core.urlresolvers import reverse

from webplatformcompat.models import Feature

from .base import APITestCase


class TestFeatureViewSet(APITestCase):
    def test_get_minimal(self):
        feature = self.create(Feature)
        url = reverse('feature-detail', kwargs={'pk': feature.pk})
        fh_pk = feature.history.all()[0].pk
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': feature.id,
            'slug': '',
            'mdn_path': None,
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': None,
            'parent': None,
            'ancestors': [feature.id],
            'siblings': [feature.id],
            'children': [],
            'descendants': [feature.id],
            'history': [fh_pk],
            'history_current': fh_pk,
        }
        self.assertDataEqual(expected_data, response.data)

        expected_json = {
            "features": {
                "id": str(feature.id),
                "slug": "",
                "mdn_path": None,
                "experimental": False,
                "standardized": True,
                "stable": True,
                "obsolete": False,
                "name": None,
                "links": {
                    "parent": None,
                    "ancestors": [str(feature.id)],
                    "siblings": [str(feature.id)],
                    "children": [],
                    "descendants": [str(feature.id)],
                    "history_current": str(fh_pk),
                    "history": [str(fh_pk)],
                },
            },
            "links": {
                "features.parent": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.parent}"),
                    "type": "features",
                },
                "features.ancestors": {
                    "href": (
                        self.baseUrl + "/api/v1/features/"
                        "{features.ancestors}"),
                    "type": "features",
                },
                "features.siblings": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.siblings}"),
                    "type": "features",
                },
                "features.children": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.children}"),
                    "type": "features",
                },
                "features.descendants": {
                    "href": (
                        self.baseUrl + "/api/v1/features/"
                        "{features.descendants}"),
                    "type": "features",
                },
                "features.history_current": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_features/"
                        "{features.history_current}"),
                    "type": "historical_features",
                },
                "features.history": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_features/"
                        "{features.history}"),
                    "type": "historical_features",
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_get_maximal(self):
        parent = self.create(Feature, slug='html-element')
        feature = self.create(
            Feature, slug='html-element-input', name={'zxx': 'input'},
            mdn_path="/en-US/docs/Web/HTML/Element/input",
            experimental=True, standardized=False, stable=False, obsolete=True,
            parent=parent)
        url = reverse('feature-detail', kwargs={'pk': feature.pk})
        fh_pk = feature.history.all()[0].pk
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': feature.id,
            'slug': 'html-element-input',
            'mdn_path': "/en-US/docs/Web/HTML/Element/input",
            'experimental': True,
            'standardized': False,
            'stable': False,
            'obsolete': True,
            'name': 'input',
            'parent': parent.id,
            'ancestors': [parent.id, feature.id],
            'siblings': [feature.id],
            'children': [],
            'descendants': [feature.id],
            'history': [fh_pk],
            'history_current': fh_pk,
        }
        self.assertDataEqual(expected_data, response.data)

        expected_json = {
            "features": {
                "id": str(feature.id),
                "slug": "html-element-input",
                "mdn_path": "/en-US/docs/Web/HTML/Element/input",
                "experimental": True,
                "standardized": False,
                "stable": False,
                "obsolete": True,
                'name': 'input',
                "links": {
                    "parent": str(parent.id),
                    "ancestors": [str(parent.id), str(feature.id)],
                    "siblings": [str(feature.id)],
                    "children": [],
                    "descendants": [str(feature.id)],
                    "history_current": str(fh_pk),
                    "history": [str(fh_pk)],
                },
            },
            "links": {
                "features.parent": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.parent}"),
                    "type": "features",
                },
                "features.ancestors": {
                    "href": (
                        self.baseUrl + "/api/v1/features/"
                        "{features.ancestors}"),
                    "type": "features",
                },
                "features.siblings": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.siblings}"),
                    "type": "features",
                },
                "features.children": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.children}"),
                    "type": "features",
                },
                "features.descendants": {
                    "href": (
                        self.baseUrl + "/api/v1/features/"
                        "{features.descendants}"),
                    "type": "features",
                },
                "features.history_current": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_features/"
                        "{features.history_current}"),
                    "type": "historical_features",
                },
                "features.history": {
                    "href": (
                        self.baseUrl + "/api/v1/historical_features/"
                        "{features.history}"),
                    "type": "historical_features",
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_slug(self):
        feature = self.create(
            Feature, slug='feature', name={'en': 'A Feature'})
        other = self.create(Feature, slug="other", name={'en': 'Other'})
        fhistory_pk = feature.history.all()[0].pk

        response = self.client.get(
            reverse('feature-list'), {'slug': 'feature'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': feature.id,
            'slug': 'feature',
            'mdn_path': None,
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': {'en': 'A Feature'},
            'parent': None,
            'ancestors': [feature.id],
            'siblings': [feature.id, other.id],
            'children': [],
            'descendants': [feature.id],
            'history': [fhistory_pk],
            'history_current': fhistory_pk,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_post_empty(self):
        self.login_superuser()
        response = self.client.post(reverse('feature-list'), {})
        self.assertEqual(400, response.status_code)
        expected_data = {
            "slug": ["This field is required."],
            "name": ["This field is required."],
        }
        self.assertDataEqual(response.data, expected_data)
