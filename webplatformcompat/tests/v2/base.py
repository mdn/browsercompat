"""Common functionality for testing the v2 API."""

from ..base import TestCase as BaseTestCase
from ..base import APITestCase as BaseAPITestCase


class NamespaceMixin(object):
    """Designate the namespace for tests."""

    namespace = 'v2'
    __test__ = True  # Run these tests if disabled in base class

    def full_api_reverse(self, viewname, **kwargs):
        """Create a full URL for a namespaced API view."""
        return 'http://testserver' + self.api_reverse(viewname, **kwargs)


class TestCase(BaseTestCase, NamespaceMixin):
    """Useful methods for testing."""


class APITestCase(BaseAPITestCase, NamespaceMixin):
    """Useful methods for testing API endpoints."""
