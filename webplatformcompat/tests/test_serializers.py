#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.serializer."""

from json import dumps

from django.core.urlresolvers import reverse

from webplatformcompat.models import (
    Browser, Feature, Maturity, Section, Specification, Version)

from .base import APITestCase


class TestHistoricalModelSerializer(APITestCase):
    """Test common serializer functionality through BrowserSerializer."""
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
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "name": {"en": "Old Name"},
            "note": None,
            'history': [h.pk for h in histories],
            'history_current': current_history.pk,
            'versions': [],
        }
        self.assertDataEqual(response.data, expected_data)

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
            'history_current': ['Invalid history ID for this object']
        }
        self.assertDataEqual(response.data, expected_data)

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
        expected_data = {
            "id": browser.pk,
            "slug": "browser",
            "name": {"en": "Browser"},
            "note": None,
            'history': [h.pk for h in histories],
            'history_current': new_history.pk,
            'versions': [],
        }
        self.assertDataEqual(response.data, expected_data)


class TestBrowserSerializer(APITestCase):
    """Test BrowserSerializer through the view."""
    def setUp(self):
        self.browser = self.create(
            Browser, slug='browser', name={'en': 'Browser'})
        self.v1 = self.create(Version, browser=self.browser, version='1.0')
        self.v2 = self.create(Version, browser=self.browser, version='2.0')
        self.url = reverse('browser-detail', kwargs={'pk': self.browser.pk})

    def test_versions_change_order(self):
        data = dumps({
            'browsers': {
                'links': {
                    'versions': [str(self.v2.pk), str(self.v1.pk)]
                }
            }
        })
        response = self.client.put(
            self.url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        expected_versions = [v.pk for v in (self.v2, self.v1)]
        actual_versions = response.data['versions']
        self.assertEqual(expected_versions, actual_versions)

    def test_versions_same_order(self):
        data = dumps({
            'browsers': {
                'links': {
                    'versions': [str(self.v1.pk), str(self.v2.pk)]
                }
            }
        })
        response = self.client.put(
            self.url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        expected_versions = [v.pk for v in (self.v1, self.v2)]
        actual_versions = response.data['versions']
        self.assertEqual(expected_versions, actual_versions)


class TestSpecificationSerializer(APITestCase):
    """Test SpecificationSerializer through the view."""

    def setUp(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        self.spec = self.create(
            Specification, maturity=maturity, slug="css3-animations",
            mdn_key='CSS3 Animations',
            name={'en': "CSS Animations"},
            uri={'en': 'http://dev.w3.org/csswg/css-animations/'})
        self.s46 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-direction' property"},
            subpath={'en': "#animation-direction"})
        self.s45 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-iteration-count' property"},
            subpath={'en': "#animation-iteration-count"})
        self.url = reverse('specification-detail', kwargs={'pk': self.spec.pk})

    def test_update_without_sections(self):
        data = dumps({
            'specifications': {
                'name': {'en': 'CSS3 Animations'}
            }
        })
        response = self.client.put(
            self.url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        spec = Specification.objects.get(id=self.spec.id)
        self.assertEqual({'en': 'CSS3 Animations'}, spec.name)

    def test_sections_change_order(self):
        data = dumps({
            'specifications': {
                'links': {
                    'sections': [str(self.s45.pk), str(self.s46.pk)]
                }
            }
        })
        response = self.client.put(
            self.url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        expected_sections = [self.s45.pk, self.s46.pk]
        actual_sections = response.data['sections']
        self.assertEqual(expected_sections, actual_sections)

    def test_sections_same_order(self):
        data = dumps({
            'specifications': {
                'links': {
                    'sections': [str(self.s46.pk), str(self.s45.pk)]
                }
            }
        })
        response = self.client.put(
            self.url, data=data, content_type='application/vnd.api+json',
            HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        expected_sections = [self.s46.pk, self.s45.pk]
        actual_sections = response.data['sections']
        self.assertEqual(expected_sections, actual_sections)


class TestUserSerializer(APITestCase):
    """Test UserSerializer through the view."""
    def test_get(self):
        self.login_user()
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, response.data)
        actual_data = response.data
        self.assertEqual(0, actual_data['agreement'])
        self.assertEqual(['change-resource'], actual_data['permissions'])


class TestHistoricalFeatureSerializer(APITestCase):
    """Test HistoricalFeatureSerializer, which has archive fields."""
    def test_get_history_no_parent(self):
        feature = self.create(
            Feature, slug="the_feature", name={"en": "The Feature"})
        history = feature.history.all()[0]
        url = reverse('historicalfeature-detail', kwargs={'pk': history.pk})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, response.data)
        actual_sections = response.data['features']['links']['sections']
        self.assertEqual([], actual_sections)
        actual_parent = response.data['features']['links']['parent']
        self.assertIsNone(actual_parent)

    def test_get_history_sections_parent(self):
        parent = self.create(
            Feature, slug="the_parent", name={"en": "The Parent"})
        feature = self.create(
            Feature, slug="the_feature", name={"en": "The Feature"},
            parent=parent)
        history = feature.history.all()[0]
        url = reverse('historicalfeature-detail', kwargs={'pk': history.pk})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, response.data)
        expected_parent = str(parent.pk)
        actual_parent = response.data['features']['links']['parent']
        self.assertEqual(expected_parent, actual_parent)
