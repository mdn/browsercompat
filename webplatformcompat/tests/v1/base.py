"""Common functionality for testing the v1 API."""

from ..base import TestCase as BaseTestCase
from ..base import APITestCase as BaseAPITestCase


class TestCase(BaseTestCase):
    """Useful methods for testing."""

    namespace = 'v1'


class APITestCase(BaseAPITestCase):
    """Useful methods for testing API endpoints."""

    namespace = 'v1'
