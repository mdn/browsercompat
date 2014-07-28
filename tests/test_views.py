#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` views module.
"""

from django.test import TestCase


class TestViews(TestCase):

    def test_home(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
