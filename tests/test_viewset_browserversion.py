#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.BrowserVersionViewSet` class.
"""
from __future__ import unicode_literals
from json import loads

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, BrowserVersion

from .base import APITestCase


class TestBrowserVersionViewSet(APITestCase):
    def test_get_minimal(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        bv = self.create(BrowserVersion, browser=browser, version='1.0')
        url = reverse('browserversion-detail', kwargs={'pk': bv.pk})
        bvh = bv.history.all()[0]
        bvh_url = self.reverse('historicalbrowserversion-detail', pk=bvh.pk)
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
            'history': [bvh_url],
            'history_current': bvh_url,
        }
        actual = dict(response.data)
        self.assertDictEqual(expected_data, actual)

        expected_json = {
            "browser-versions": {
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
                    "history_current": str(bvh.pk),
                    "history": [str(bvh.pk)],
                },
            },
            "links": {
                "browser-versions.browser": {
                    "href": (
                        "http://testserver/api/browsers/"
                        "{browser-versions.browser}"),
                    "type": "browsers"
                },
                "browser-versions.history_current": {
                    "href": (
                        "http://testserver/api/historical-browser-versions/"
                        "{browser-versions.history_current}"),
                    "type": "historical-browser-versions"
                },
                "browser-versions.history": {
                    "href": (
                        "http://testserver/api/historical-browser-versions/"
                        "{browser-versions.history}"),
                    "type": "historical-browser-versions"
                },
            }
        }
        self.assertDictEqual(
            expected_json, loads(response.content.decode('utf-8')))

    def test_filter_by_browser(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        bversion = self.create(BrowserVersion, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(BrowserVersion, browser=other, version="2.0")
        bvhistory = bversion.history.all()[0]
        bvhistory_url = self.reverse(
            'historicalbrowserversion-detail', pk=bvhistory.pk)

        response = self.client.get(
            reverse('browserversion-list'), {'browser': browser.pk})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': bversion.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [bvhistory_url],
            'history_current': bvhistory_url,
        }]
        self.assertEqual([dict(x) for x in response.data], expected_data)

    def test_filter_by_browser_slug(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        bversion = self.create(BrowserVersion, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(BrowserVersion, browser=other, version="2.0")
        bvhistory = bversion.history.all()[0]
        bvhistory_url = self.reverse(
            'historicalbrowserversion-detail', pk=bvhistory.pk)

        response = self.client.get(
            reverse('browserversion-list'),
            {'browser__slug': 'firefox'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': bversion.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [bvhistory_url],
            'history_current': bvhistory_url,
        }]
        self.assertEqual([dict(x) for x in response.data], expected_data)

    def test_filter_by_version(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        bversion = self.create(BrowserVersion, browser=browser, version="1.0")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(BrowserVersion, browser=other, version="2.0")
        bvhistory = bversion.history.all()[0]
        bvhistory_url = self.reverse(
            'historicalbrowserversion-detail', pk=bvhistory.pk)

        response = self.client.get(
            reverse('browserversion-list'), {'version': '1.0'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': bversion.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'unknown',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [bvhistory_url],
            'history_current': bvhistory_url,
        }]
        self.assertEqual([dict(x) for x in response.data], expected_data)

    def test_filter_by_status(self):
        browser = self.create(Browser, slug="firefox", name={'en': 'Firefox'})
        bversion = self.create(
            BrowserVersion, browser=browser, version="1.0", status="current")
        other = self.create(Browser, slug="o", name={'en': 'Other'})
        self.create(
            BrowserVersion, browser=other, version="2.0", status="unknown")
        bvhistory = bversion.history.all()[0]
        bvhistory_url = self.reverse(
            'historicalbrowserversion-detail', pk=bvhistory.pk)

        response = self.client.get(
            reverse('browserversion-list'), {'status': 'current'})
        self.assertEqual(200, response.status_code, response.data)
        expected_data = [{
            'id': bversion.id,
            'version': '1.0',
            'release_day': None,
            'retirement_day': None,
            'status': 'current',
            'release_notes_uri': None,
            'note': None,
            'order': 0,
            'browser': self.reverse('browser-detail', pk=browser.pk),
            'history': [bvhistory_url],
            'history_current': bvhistory_url,
        }]
        self.assertEqual([dict(x) for x in response.data], expected_data)
