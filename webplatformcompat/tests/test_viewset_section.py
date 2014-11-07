#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.SectionViewSet` class."""
from __future__ import unicode_literals
from json import loads

from django.core.urlresolvers import reverse

from webplatformcompat.models import Maturity, Section, Specification

from .base import APITestCase


class TestSectionViewSet(APITestCase):
    def test_get(self):
        maturity = self.create(
            Maturity, slug='REC', name={'en': 'Recommendation'})
        spec = self.create(
            Specification, maturity=maturity, slug="css1",
            name={'en': "CSS Level&nbsp;1"},
            uri={'en': 'http://www.w3.org/TR/CSS1/'})
        section = self.create(
            Section, specification=spec,
            number={'en': '5.6.1'}, name={'en': "display"},
            subpath={'en': '#display'})
        url = reverse('section-detail', kwargs={'pk': section.pk})
        history_pk = section.history.all()[0].pk
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': section.id,
            'number': {'en': '5.6.1'},
            'name': {'en': 'display'},
            'subpath': {'en': '#display'},
            'note': None,
            'specification': spec.pk,
            'features': [],
            'history': [history_pk],
            'history_current': history_pk,
        }
        self.assertDataEqual(expected_data, response.data)

        expected_json = {
            "sections": {
                "id": str(section.id),
                'number': {'en': '5.6.1'},
                'name': {'en': 'display'},
                'subpath': {'en': '#display'},
                'note': None,
                "links": {
                    "specification": str(spec.pk),
                    "features": [],
                    "history_current": str(history_pk),
                    "history": [str(history_pk)],
                },
            },
            "links": {
                "sections.specification": {
                    "href": (
                        "http://testserver/api/v1/specifications/"
                        "{sections.specification}"),
                    "type": "specifications"
                },
                "sections.features": {
                    "href": (
                        "http://testserver/api/v1/features/"
                        "{sections.features}"),
                    "type": "features",
                },
                "sections.history_current": {
                    "href": (
                        "http://testserver/api/v1/historical_sections/"
                        "{sections.history_current}"),
                    "type": "historical_sections"
                },
                "sections.history": {
                    "href": (
                        "http://testserver/api/v1/historical_sections/"
                        "{sections.history}"),
                    "type": "historical_sections"
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)
