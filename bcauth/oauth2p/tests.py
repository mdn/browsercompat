# -*- coding: utf-8 -*-
"""Tests for oauth2_provider overrides."""

from __future__ import unicode_literals

from django.test import RequestFactory
from oauth2_provider.exceptions import FatalClientError, OAuthToolkitError
from oauth2_provider.http import HttpResponseUriRedirect

from webplatformcompat.tests.base import TestCase
from .views import MyAuthorizationView


class FakeOAuthLibError(object):
    """A fake oauthlib error passed to OAuthToolkitError."""

    def __init__(self, redirect_uri='/redirect', urlencoded=None, **kwargs):
        """Initialize the fake error."""
        self.redirect_uri = redirect_uri
        self.urlencoded = urlencoded or 'fake=1'
        for name, value in kwargs.items():
            setattr(self, name, value)


class TestMyAuthorizationView(TestCase):
    """Test our overrides of the AuthorizationView."""

    def setUp(self):
        self.view = MyAuthorizationView()
        self.view.request = RequestFactory().get('/authorize')

    def test_error_response_without_redirect(self):
        """Test that errors are rendered without a 'url' context variable."""
        base_error = FakeOAuthLibError(status_code=405)
        error = FatalClientError(error=base_error)
        response = self.view.error_response(error)
        self.assertNotIn('url', response.context_data)

    def test_error_response_with_redirect(self):
        """Test that errors are rendered without a 'url' context variable."""
        base_error = FakeOAuthLibError()
        error = OAuthToolkitError(error=base_error)
        response = self.view.error_response(error)
        self.assertIsInstance(response, HttpResponseUriRedirect)
