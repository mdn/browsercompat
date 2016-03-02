# -*- coding: utf-8 -*-
"""Tests for simple history overrides in v2 API."""

from ..test_history import TestBaseMiddleware
from .base import NamespaceMixin


class TestMiddleware(NamespaceMixin, TestBaseMiddleware):
    """Test the Middleware using v2 API endpoints."""

    def api_data(self):
        """Return JSON data for creating a new browser."""
        return {
            'data': {
                'type': 'browsers',
                'attributes': {
                    'slug': 'firefox',
                    'name': {
                        'en': 'Firefox'
                    }
                }
            }
        }
