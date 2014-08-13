#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_web-platform-compat
------------

Tests for `web-platform-compat` models module.
"""

import unittest

from webplatformcompat.models import Browser, BrowserVersion


class TestBrowser(unittest.TestCase):

    def test_str(self):
        browser = Browser(slug="browser")
        self.assertEqual('browser', str(browser))


class TestBrowserVersion(unittest.TestCase):

    def test_str(self):
        browser = Browser(slug="browser")
        bv = BrowserVersion(browser=browser, version='1.0')
        self.assertEqual('browser 1.0', str(bv))
