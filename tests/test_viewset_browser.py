#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat.viewsets.BrowserViewSet` class.
"""
from __future__ import unicode_literals
from json import dumps, loads

from django.core.urlresolvers import reverse

from webplatformcompat.models import Browser, BrowserVersion

from .base import APITestCase


class TestBrowserViewset(APITestCase):
    '''Test browsers list and detail, as well as common functionality'''

    def test_get_empty(self):
        browser = self.create(Browser)
        url = self.reverse('browser-detail', pk=browser.pk)
        response = self.client.get(
            url, content_type="application/vnd.api+json")
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = {
            'id': browser.pk,
            'slug': '',
            'icon': None,
            'name': None,
            'note': None,
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }
        self.assertEqual(dict(response.data), expected_data)
        expected_content = {
            "browsers": {
                "id": str(browser.pk),
                "slug": "",
                "icon": None,
                "name": None,
                "note": None,
                "links": {
                    "history": [str(history.pk)],
                    "history_current": str(history.pk),
                    "versions": [],
                }
            },
            "links": {
                "browsers.history": {
                    "type": "historical-browsers",
                    "href": history_url.replace(
                        str(history.pk), "{browsers.history}"),
                },
                "browsers.history_current": {
                    "type": "historical-browsers",
                    "href": history_url.replace(
                        str(history.pk), "{browsers.history_current}"),
                },
                "browsers.versions": {
                    'href': (
                        'http://testserver/api/browser-versions/'
                        '{browsers.versions}'),
                    "type": "browser-versions",
                },
            }
        }
        actual_content = loads(response.content.decode('utf-8'))
        self.assertEqual(expected_content, actual_content)

    def test_get_populated(self):
        browser = self.create(
            Browser,
            slug="firefox",
            icon=("https://people.mozilla.org/~faaborg/files/shiretoko"
                  "/firefoxIcon/firefox-128.png"),
            name={"en": "Firefox"},
            note={"en": "Uses Gecko for its web browser engine"})
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.get(url)
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = {
            'id': browser.pk,
            'slug': 'firefox',
            'icon': ("https://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': {"en": "Firefox"},
            'note': {"en": "Uses Gecko for its web browser engine"},
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }
        self.assertEqual(response.data, expected_data)

    def test_get_list(self):
        firefox = self.create(
            Browser,
            slug="firefox", name={"en": "Firefox"},
            icon=("https://people.mozilla.org/~faaborg/files/shiretoko"
                  "/firefoxIcon/firefox-128.png"),
            note={"en": "Uses Gecko for its web browser engine"})
        chrome = self.create(Browser, slug="chrome", name={"en": "Chrome"})
        response = self.client.get(reverse('browser-list'))
        firefox_history_id = '%s' % firefox.history.get().pk
        chrome_history_id = '%s' % chrome.history.get().pk
        expected_content = {
            'browsers': [
                {
                    'id': '%s' % firefox.pk,
                    'slug': 'firefox',
                    'icon': ("https://people.mozilla.org/~faaborg/files/"
                             "shiretoko/firefoxIcon/firefox-128.png"),
                    'name': {"en": "Firefox"},
                    'note': {"en": "Uses Gecko for its web browser engine"},
                    'links': {
                        'history': [firefox_history_id],
                        'history_current': firefox_history_id,
                        'versions': [],
                    },
                }, {
                    'id': '%s' % chrome.pk,
                    'slug': 'chrome',
                    'icon': None,
                    'name': {"en": "Chrome"},
                    'note': None,
                    'links': {
                        'history': [chrome_history_id],
                        'history_current': chrome_history_id,
                        'versions': [],
                    },
                },
            ],
            'links': {
                'browsers.history': {
                    'href': (
                        'http://testserver/api/historical-browsers/'
                        '{browsers.history}'),
                    'type': 'historical-browsers',
                },
                'browsers.history_current': {
                    'href': (
                        'http://testserver/api/historical-browsers/'
                        '{browsers.history_current}'),
                    'type': 'historical-browsers',
                },
                'browsers.versions': {
                    'href': (
                        'http://testserver/api/browser-versions/'
                        '{browsers.versions}'),
                    'type': 'browser-versions',
                },
            }
        }
        actual_content = loads(response.content.decode('utf-8'))
        self.assertEqual(expected_content, actual_content)

    def test_filter_by_slug(self):
        browser = self.create(
            Browser, slug="firefox", icon='', name={"en": "Firefox"},
            note=None)
        self.create(
            Browser, slug="chrome", icon='', name={"en": "Chrome"})
        url = reverse('browser-list')
        response = self.client.get(url, {'slug': 'firefox'})
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = [{
            'id': browser.pk,
            'slug': 'firefox',
            'icon': None,
            'name': {"en": "Firefox"},
            'note': None,
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }]
        self.assertEqual(response.data, expected_data)

    def test_get_browsable_api(self):
        browser = self.create(Browser)
        url = self.reverse('browser-list')
        response = self.client.get(url, HTTP_ACCEPT="text/html")
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = [{
            'id': browser.pk,
            'slug': '',
            'icon': None,
            'name': None,
            'note': None,
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }]
        self.assertEqual(list(response.data), expected_data)
        self.assertTrue(response['content-type'].startswith('text/html'))

    def test_post_not_authorized(self):
        response = self.client.post(reverse('browser-list'), {})
        self.assertEqual(403, response.status_code)
        expected_data = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, expected_data)

    def test_post_empty(self):
        self.login_superuser()
        response = self.client.post(reverse('browser-list'), {})
        self.assertEqual(400, response.status_code)
        expected_data = {
            "slug": ["This field is required."],
            "name": ["This field is required."],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_minimal(self):
        self.login_superuser()
        data = {'slug': 'firefox', 'name': '{"en": "Firefox"}'}
        response = self.client.post(reverse('browser-list'), data)
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = {
            "id": browser.pk,
            "slug": "firefox",
            "icon": None,
            "name": {"en": "Firefox"},
            "note": None,
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_minimal_json_api(self):
        self.login_superuser()
        data = dumps({
            'browsers': {
                'slug': 'firefox',
                'name': {
                    "en": "Firefox"
                },
            }
        })
        response = self.client.post(
            reverse('browser-list'), data=data,
            content_type="application/vnd.api+json")
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = {
            "id": browser.pk,
            "slug": "firefox",
            "icon": None,
            "name": {"en": "Firefox"},
            "note": None,
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_full(self):
        self.login_superuser()
        data = {
            'slug': 'firefox',
            'icon': ("https://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': '{"en": "Firefox"}',
            'note': '{"en": "Uses Gecko for its web browser engine"}',
        }
        response = self.client.post(reverse('browser-list'), data)
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        history = browser.history.get()
        history_url = self.reverse('historicalbrowser-detail', pk=history.pk)
        expected_data = {
            'id': browser.pk,
            'slug': 'firefox',
            'icon': ("https://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': {"en": "Firefox"},
            'note': {"en": "Uses Gecko for its web browser engine"},
            'history': [history_url],
            'history_current': history_url,
            'versions': [],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_bad_data(self):
        self.login_superuser()
        data = {
            'slug': 'bad slug',
            'icon': ("http://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': '"Firefox"',
            'note': '{"es": "Utiliza Gecko por su motor del navegador web"}',
        }
        response = self.client.post(reverse('browser-list'), data)
        self.assertEqual(400, response.status_code, response.data)
        expected_data = {
            'slug': [
                "Enter a valid 'slug' consisting of letters, numbers,"
                " underscores or hyphens."],
            'icon': ["URI must use the 'https' protocol."],
            'name': [
                "Value must be a JSON dictionary of language codes to"
                " strings."],
            'note': ["Missing required language code 'en'."],
        }
        self.assertEqual(response.data, expected_data)

    def test_put_as_json_api(self):
        '''If content is application/vnd.api+json, put is partial'''
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        data = dumps({
            'browsers': {
                'name': {
                    'en': 'New Name'
                }
            }
        })
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data, content_type="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)
        histories = browser.history.all()
        current_history = histories[0]
        view = 'historicalbrowser-detail'
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "icon": None,
            "name": {"en": "New Name"},
            "note": None,
            "history": [
                self.reverse(view, pk=h.pk) for h in histories],
            "history_current": self.reverse(view, pk=current_history.pk),
            "versions": [],
        }
        self.assertEqual(response.data, expected_data)

    def test_put_as_json(self):
        '''If content is application/json, put is full put'''
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        data = {'name': '{"en": "New Name"}'}
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data)
        self.assertEqual(400, response.status_code, response.data)
        expected_data = {
            "slug": ["This field is required."],
        }
        self.assertEqual(response.data, expected_data)

    def test_put_history_current(self):
        browser = self.create(Browser, slug='browser', name={'en': 'Old Name'})
        old_history = browser.history.latest('history_date')
        browser.name = {'en': 'Browser'}
        browser.save()
        data = dumps({
            'browsers': {
                'links': {
                    'history_current': str(old_history.history_id)
                }
            }
        })
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data, content_type="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)
        current_history = browser.history.all()[0]
        self.assertNotEqual(old_history.history_id, current_history.history_id)
        histories = browser.history.all()
        self.assertEqual(3, len(histories))
        view = 'historicalbrowser-detail'
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "icon": None,
            "name": {"en": "Old Name"},
            "note": None,
            'history': [
                self.reverse(view, pk=h.pk) for h in histories],
            'history_current': self.reverse(view, pk=current_history.pk),
            'versions': [],
        }
        self.assertEqual(dict(response.data), expected_data)

    def test_put_history_current_wrong_browser_fails(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        other_browser = self.create(
            Browser, slug='other-browser', name={'en': 'Other Browser'})
        bad_history = other_browser.history.all()[0]
        data = dumps({
            'browsers': {
                'slug': 'browser',
                'links': {
                    'history_current': str(bad_history.history_id)
                }
            }
        })
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data, content_type="application/vnd.api+json")
        self.assertEqual(400, response.status_code, response.data)
        expected_data = {
            'history_current': ['history is for a different object']
        }
        self.assertEqual(dict(response.data), expected_data)

    def test_put_history_same(self):
        browser = self.create(Browser, slug='browser', name={'en': 'Old Name'})
        browser.name = {'en': 'Browser'}
        browser.save()
        current_history = browser.history.latest('history_date')
        data = dumps({
            'browsers': {
                'links': {
                    'history_current': str(current_history.history_id)
                }
            }
        })
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data, content_type="application/vnd.api+json")
        self.assertEqual(200, response.status_code, response.data)
        new_history = browser.history.all()[0]
        self.assertNotEqual(new_history.history_id, current_history.history_id)
        histories = browser.history.all()
        self.assertEqual(3, len(histories))
        view = 'historicalbrowser-detail'
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "icon": None,
            "name": {"en": "Browser"},
            "note": None,
            'history': [
                self.reverse(view, pk=h.pk) for h in histories],
            'history_current': self.reverse(view, pk=new_history.pk),
            'versions': [],
        }
        self.assertEqual(dict(response.data), expected_data)

    def test_versions_are_ordered(self):
        browser = self.create(Browser, slug='browser', name={'en': 'Browser'})
        v2 = self.create(BrowserVersion, browser=browser, version='2.0')
        v1 = self.create(BrowserVersion, browser=browser, version='1.0')
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.get(url, HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        history = browser.history.all()
        history_view = 'historicalbrowser-detail'
        version_view = 'browserversion-detail'
        expected_data = {
            "id": browser.pk,
            "slug": 'browser',
            "icon": None,
            "name": {"en": "Browser"},
            "note": None,
            "history": [
                self.reverse(history_view, pk=h.pk) for h in history],
            "history_current": self.reverse(history_view, pk=history[0].pk),
            "versions": [
                self.reverse(version_view, pk=v.pk) for v in (v2, v1)],
        }
        self.assertEqual(dict(response.data), expected_data)

    def test_versions_are_reordered(self):
        browser = self.create(Browser, slug='browser', name={'en': 'Browser'})
        v1 = self.create(BrowserVersion, browser=browser, version='1.0')
        v2 = self.create(BrowserVersion, browser=browser, version='2.0')
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        data = dumps({
            'browsers': {
                'links': {
                    'versions': [str(v1.pk), str(v2.pk)]
                }
            }
        })
        response = self.client.put(
            url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        history = browser.history.all()
        history_view = 'historicalbrowser-detail'
        version_view = 'browserversion-detail'
        expected_data = {
            "id": browser.pk,
            "slug": 'browser',
            "icon": None,
            "name": {"en": "Browser"},
            "note": None,
            "history": [
                self.reverse(history_view, pk=h.pk) for h in history],
            "history_current": self.reverse(history_view, pk=history[0].pk),
            "versions": [
                self.reverse(version_view, pk=v.pk) for v in (v1, v2)],
        }
        self.assertEqual(dict(response.data), expected_data)

    def test_versions_same_order(self):
        browser = self.create(Browser, slug='browser', name={'en': 'Browser'})
        v1 = self.create(BrowserVersion, browser=browser, version='1.0')
        v2 = self.create(BrowserVersion, browser=browser, version='2.0')
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        data = dumps({
            'browsers': {
                'links': {
                    'versions': [str(v2.pk), str(v1.pk)]
                }
            }
        })
        response = self.client.put(
            url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        history = browser.history.all()
        history_view = 'historicalbrowser-detail'
        version_view = 'browserversion-detail'
        expected_data = {
            "id": browser.pk,
            "slug": 'browser',
            "icon": None,
            "name": {"en": "Browser"},
            "note": None,
            "history": [
                self.reverse(history_view, pk=h.pk) for h in history],
            "history_current": self.reverse(history_view, pk=history[0].pk),
            "versions": [
                self.reverse(version_view, pk=v.pk) for v in (v2, v1)],
        }
        self.assertEqual(dict(response.data), expected_data)
