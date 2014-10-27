#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat` renderers module."""

from django.test import TestCase

from webplatformcompat.models import Browser
from webplatformcompat.renderers import JsonApiRenderer


class TestJsonApiRenderers(TestCase):

    def setUp(self):
        self.renderer = JsonApiRenderer()

    def test_model_to_resource_type(self):
        self.assertEqual(
            'browsers', self.renderer.model_to_resource_type(Browser()))
        self.assertEqual(
            'historical_browsers',
            self.renderer.model_to_resource_type(Browser().history.model))
        self.assertEqual(
            'data',
            self.renderer.model_to_resource_type(None))
