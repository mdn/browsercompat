#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.VersionViewSet` class.
"""
from __future__ import unicode_literals
from json import loads

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, Version

from .base import APITestCase


class TestVersionViewSet(APITestCase):
    def test_get_minimal(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        bv = self.create(Version, browser=browser, version='1.0')
        url = reverse('version-detail', kwargs={'pk': bv.pk})
        vh = bv.history.all()[0]
        vh_url = self.reverse('historicalversion-detail', pk=vh.pk)
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)

        expected_data = {
            'id': bv.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [vh_url],
            'history_current': vh_url,
        }
        self.assertDataEqual(expected_data, response.data)

        expected_json = {
            "versions": {
                "id": str(bv.id),
                "version": "1.0",
                "release_day": None,
                "retirement_day": None,
                "status": "unknown",
                "release_notes_uri": None,
                "note": None,
                "order": 0,
                "links": {
                    "browser": str(browser.pk),
                    "history_current": str(vh.pk),
                    "history": [str(vh.pk)],
                },
            },
            "links": {
                "versions.browser": {
                    "href": (
                        "http://testserver/api/v1/browsers/"
                        "{versions.browser}"),
                    "type": "browsers"
                },
                "versions.history_current": {
                    "href": (
                        "http://testserver/api/v1/historical_versions/"
                        "{versions.history_current}"),
                    "type": "historical_versions"
                },
                "versions.history": {
                    "href": (
                        "http://testserver/api/v1/historical_versions/"
                        "{versions.history}"),
                    "type": "historical_versions"
                },
            }
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_filter_by_browser(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        version = self.create(Version, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(Version, browser=other, version="2.0")
        vhistory = version.history.all()[0]
        vhistory_url = self.reverse(
            'historicalversion-detail', pk=vhistory.pk)

        response = self.client.get(
            reverse('version-list'), {'browser': browser.pk})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': version.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [vhistory_url],
            'history_current': vhistory_url,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_filter_by_browser_slug(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        version = self.create(Version, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(Version, browser=other, version="2.0")
        vhistory = version.history.all()[0]
        vhistory_url = self.reverse(
            'historicalversion-detail', pk=vhistory.pk)

        response = self.client.get(
            reverse('version-list'),
            {'browser__slug': 'firefox'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': version.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [vhistory_url],
            'history_current': vhistory_url,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_filter_by_version(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        version = self.create(Version, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(Version, browser=other, version="2.0")
        vhistory = version.history.all()[0]
        vhistory_url = self.reverse(
            'historicalversion-detail', pk=vhistory.pk)

        response = self.client.get(
            reverse('version-list'), {'version': '1.0'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': version.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [vhistory_url],
            'history_current': vhistory_url,
        }]
        self.assertDataEqual(response.data, expected_data)

    def test_filter_by_status(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        version = self.create(
            Version, browser=browser, version="1.0", status="current")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(
            Version, browser=other, version="2.0", status="unknown")
        vhistory = version.history.all()[0]
        vhistory_url = self.reverse(
            'historicalversion-detail', pk=vhistory.pk)

        response = self.client.get(
            reverse('version-list'), {'status': 'current'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': version.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'current',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [vhistory_url],
            'history_current': vhistory_url,
        }]
        self.assertDataEqual(response.data, expected_data)
