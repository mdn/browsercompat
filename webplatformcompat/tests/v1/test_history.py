# -*- coding: utf-8 -*-
"""Tests for simple history overrides in v1 API."""

from ..test_history import TestBaseMiddleware
from .base import NamespaceMixin


class TestMiddleware(NamespaceMixin, TestBaseMiddleware):
    """Test the Middleware using v1 API endpoints."""

    def api_data(self):
        """Return JSON data for creating a new browser."""
        return {
            'browsers': {
                'slug': 'firefox',
                'name': {
                    'en': 'Firefox'
                }
            }
        }
