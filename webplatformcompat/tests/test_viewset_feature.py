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
            'children': [],
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
                    "children": [],
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
                "features.children": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.children}"),
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
            'children': [],
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
                    "children": [],
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
                "features.children": {
                    "href": (
                        self.baseUrl + "/api/v1/features/{features.children}"),
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
        self.create(Feature, slug="other", name={'en': 'Other'})
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
            'children': [],
            'history': [fhistory_pk],
            'history_current': fhistory_pk,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_filter_by_parent(self):
        parent = self.create(Feature, slug='parent', name={'en': 'Parent'})
        feature = self.create(
            Feature, slug='feature', parent=parent, name={'en': 'A Feature'})
        self.create(Feature, slug="other", name={'en': 'Other'})
        fhistory_pk = feature.history.all()[0].pk

        response = self.client.get(
            reverse('feature-list'), {'parent': str(parent.id)})
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
            'parent': parent.id,
            'children': [],
            'history': [fhistory_pk],
            'history_current': fhistory_pk,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_filter_by_no_parent(self):
        parent = self.create(Feature, slug='parent', name={'en': 'Parent'})
        feature = self.create(
            Feature, slug='feature', parent=parent, name={'en': 'The Feature'})
        other = self.create(Feature, slug="other", name={'en': 'Other'})
        phistory_pk = parent.history.all()[0].pk
        ohistory_pk = other.history.all()[0].pk

        response = self.client.get(
            reverse('feature-list'), {'parent': ''})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': parent.id,
            'slug': 'parent',
            'mdn_path': None,
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': {'en': 'Parent'},
            'parent': None,
            'children': [feature.id],
            'history': [phistory_pk],
            'history_current': phistory_pk,
        }, {
            'id': other.id,
            'slug': 'other',
            'mdn_path': None,
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': {'en': 'Other'},
            'parent': None,
            'children': [],
            'history': [ohistory_pk],
            'history_current': ohistory_pk,
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
