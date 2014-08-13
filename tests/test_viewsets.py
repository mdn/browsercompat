#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` viewsets module.
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from webplatformcompat.models import Browser


class TestBrowserViewset(APITestCase):

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
        user = User.objects.create(
            username='staff', is_staff=True, is_superuser=True)
        user.set_password('5T@FF')
        user.save()
        self.assertTrue(self.client.login(username='staff', password='5T@FF'))
        response = self.client.post(reverse('browser-list'), {})
        self.assertEqual(400, response.status_code)
        expected_data = {
            "slug": [u"This field is required."],
            "name": [u"This field is required."],
        }
        self.assertEqual(response.data, expected_data)

    def test_post_minimal(self):
        user = User.objects.create(
            username='staff', is_staff=True, is_superuser=True)
        user.set_password('5T@FF')
        user.save()
        self.assertTrue(self.client.login(username='staff', password='5T@FF'))
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
        user = User.objects.create(
            username='staff', is_staff=True, is_superuser=True)
        user.set_password('5T@FF')
        user.save()
        self.assertTrue(self.client.login(username='staff', password='5T@FF'))
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
