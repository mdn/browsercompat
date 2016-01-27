# -*- coding: utf-8 -*-
"""Tests for simple history overrides in v2 API."""

from ..test_history import TestMiddleware
from .base import NamespaceMixin


class TestMiddlewareInV2(TestMiddleware, NamespaceMixin):
    """Test the Middleware using API endpoints."""
