# -*- coding: utf-8 -*-
"""Tests for view serializers."""

from ..test_view_serializers import (
    TestBaseViewFeatureViewSet, TestBaseViewFeatureUpdates)
from .base import NamespaceMixin


class TestViewFeatureViewSet(TestBaseViewFeatureViewSet, NamespaceMixin):
    """Test ViewFeaturesViewSet read operations."""


class TestViewFeatureUpdates(TestBaseViewFeatureUpdates):
    """Test ViewFeaturesViewSet update operations."""
