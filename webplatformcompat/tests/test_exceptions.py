# -*- coding: utf-8 -*-
"""Tests for API exceptions."""

from rest_framework.exceptions import ParseError

from ..exceptions import handler
from .base import TestCase


class TestExceptionHandler(TestCase):
    """Test the extended exception handler."""

    def test_api_exception(self):
        """Test the response includes 'standard' exceptions as an attribute."""
        exception = ParseError()
        response = handler(exception, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.exc, exception)

    def test_unexpected_exception(self):
        """Test that unexpected responses return None."""
        response = handler(ValueError('unexpected'), {})
        self.assertIsNone(response)
