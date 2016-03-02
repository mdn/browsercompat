# -*- coding: utf-8 -*-
"""Tests for simple_history extensions."""

from json import dumps, loads

from django.contrib.auth.models import User

from webplatformcompat.history import Changeset
from webplatformcompat.models import Browser

from .base import APITestCase


class TestBaseMiddleware(APITestCase):
    """Test the HistoryChangesetRequestMiddleware.

    This should be tested by a subclass that defines:
    * namespace - the API namespace, such as v1
    * api_data - A function returning data in the API format
    """

    __test__ = False  # Don't test outside of a versioned API
    content_type = 'application/vnd.api+json'

    def url(self, changeset):
        """Return the test URL."""
        return (
            self.api_reverse('browser-list') +
            '?use_changeset=%s' % changeset.id)

    def test_post_with_changeset(self):
        self.login_user()
        changeset = Changeset.objects.create(user=self.user)
        url = self.url(changeset)
        response = self.client.post(
            url, dumps(self.api_data()), content_type=self.content_type)
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        history = browser.history.get()
        self.assertEqual(changeset.id, history.history_changeset_id)

    def test_post_with_changeset_wrong_user(self):
        self.login_user()
        other = User.objects.create(username='other')
        changeset = Changeset.objects.create(user=other)
        url = self.url(changeset)
        response = self.client.post(
            url, dumps(self.api_data()), content_type=self.content_type)
        self.assertEqual(400, response.status_code)
        expected = {
            'errors': {
                'changeset': (
                    'Changeset %s has a different user.' % changeset.id)
            }
        }
        self.assertDataEqual(expected, loads(response.content.decode('utf-8')))

    def test_post_with_closed_changeset(self):
        self.login_user()
        changeset = Changeset.objects.create(user=self.user, closed=True)
        url = self.url(changeset)
        response = self.client.post(
            url, dumps(self.api_data()), content_type=self.content_type)
        self.assertEqual(400, response.status_code)
        expected = {
            'errors': {
                'changeset': 'Changeset %s is closed.' % changeset.id}}
        self.assertDataEqual(expected, loads(response.content.decode('utf-8')))

    def test_post_with_error_not_json_api(self):
        self.login_user()
        changeset = Changeset.objects.create(user=self.user, closed=True)
        url = self.url(changeset)
        data = {'slug': 'firefox', 'name': '{"en": "Firefox"}'}
        response = self.client.post(url, data)
        self.assertEqual(400, response.status_code)
        expected = 'Changeset %s is closed.' % changeset.id
        self.assertDataEqual(expected, response.content.decode('utf-8'))
