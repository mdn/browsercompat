"""Common functionality for testing the v1 API."""

from ..base import TestCase as BaseTestCase
from ..base import APITestCase as BaseAPITestCase


class NamespaceMixin(object):
    """Designate the namespace for tests."""

    namespace = 'v1'
    __test__ = True  # Run these tests if disabled in base class


class TestCase(BaseTestCase, NamespaceMixin):
    """Useful methods for testing."""


class APITestCase(BaseAPITestCase, NamespaceMixin):
    """Useful methods for testing API endpoints."""
