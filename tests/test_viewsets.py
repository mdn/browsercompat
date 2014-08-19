#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` viewsets module.
"""
from __future__ import unicode_literals
from json import dumps

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from webplatformcompat.models import Browser


class TestBrowserViewset(APITestCase):

    def login_superuser(self):
        user = User.objects.create(
            username='staff', is_staff=True, is_superuser=True)
        user.set_password('5T@FF')
        user.save()
        self.assertTrue(self.client.login(username='staff', password='5T@FF'))
        return user

    def test_get_empty(self):
        browser = Browser.objects.create()
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.get(url)
        expected_data = {
            'id': browser.pk,
            'slug': '',
            'icon': None,
            'name': None,
            'note': None}
        self.assertEqual(response.data, expected_data)

    def test_get_populated(self):
        browser = Browser.objects.create(
            slug="firefox",
            icon=("https://people.mozilla.org/~faaborg/files/shiretoko"
                  "/firefoxIcon/firefox-128.png"),
            name={"en": "Firefox"},
            note={"en": "Uses Gecko for its web browser engine"})
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.get(url)
        expected_data = {
            'id': browser.pk,
            'slug': 'firefox',
            'icon': ("https://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': {"en": "Firefox"},
            'note': {"en": "Uses Gecko for its web browser engine"},
        }
        self.assertEqual(response.data, expected_data)

    def test_post_not_authorized(self):
        response = self.client.post(reverse('browser-list'), {})
        self.assertEqual(403, response.status_code)
        expected_data = {
            u'detail': u'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, expected_data)

    def test_post_empty(self):
        self.login_superuser()
        response = self.client.post(reverse('browser-list'), {})
        self.assertEqual(400, response.status_code)
        expected_data = {
            "slug": [u"This field is required."],
            "name": [u"This field is required."],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_minimal(self):
        self.login_superuser()
        data = {'slug': 'firefox', 'name': '{"en": "Firefox"}'}
        response = self.client.post(reverse('browser-list'), data)
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        expected_data = {
            "id": browser.pk,
            "slug": "firefox",
            "icon": None,
            "name": {u"en": u"Firefox"},
            "note": None
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
        expected_data = {
            'id': browser.pk,
            'slug': 'firefox',
            'icon': ("https://people.mozilla.org/~faaborg/files/shiretoko"
                     "/firefoxIcon/firefox-128.png"),
            'name': {"en": "Firefox"},
            'note': {"en": "Uses Gecko for its web browser engine"},
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
        self.login_superuser()
        browser = Browser.objects.create(
            slug='browser', name={'en': 'Old Name'})
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
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "icon": None,
            "name": {"en": "New Name"},
            "note": None,
        }
        self.assertEqual(response.data, expected_data)

    def test_put_as_json(self):
        '''If content is application/json, put is full put'''
        self.login_superuser()
        browser = Browser.objects.create(
            slug='browser', name={'en': 'Old Name'})
        data = {'name': '{"en": "New Name"}'}
        url = reverse('browser-detail', kwargs={'pk': browser.pk})
        response = self.client.put(
            url, data=data)
        self.assertEqual(400, response.status_code, response.data)
        expected_data = {
            "slug": ["This field is required."],
        }
        self.assertEqual(response.data, expected_data)
