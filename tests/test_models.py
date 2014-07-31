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
        browser = Browser(name='The Browser')
        self.assertEqual('The Browser', str(browser))


class TestBrowserVersion(unittest.TestCase):

    def test_str(self):
        browser = Browser(name='The Browser')
        bv = BrowserVersion(browser=browser, version='1.0')
        self.assertEqual('The Browser 1.0', str(bv))
