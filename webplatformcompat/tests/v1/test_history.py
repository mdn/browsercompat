# -*- coding: utf-8 -*-
"""Tests for simple history overrides in v1 API."""

from ..test_history import TestMiddleware


class TestMiddlewareInV1(TestMiddleware):
    """Test the Middleware using v1 API endpoints."""

    __test__ = True  # Run these tests
    namespace = 'v1'  # Use the v1 API endpoints
