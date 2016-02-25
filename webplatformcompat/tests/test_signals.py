# -*- coding: utf-8 -*-
"""Tests for API signal handlers."""
import mock
import unittest

from webplatformcompat.models import Browser, Maturity
from webplatformcompat.signals import post_save_update_cache
from .base import TestCase


class TestDeleteSignal(TestCase):
    def setUp(self):
        patcher = mock.patch(
            'webplatformcompat.signals.update_cache_for_instance')
        self.login_user()
        self.mocked_update_cache = patcher.start()
        self.addCleanup(patcher.stop)
        self.maturity = self.create(Maturity, slug='foo')
        self.mocked_update_cache.reset_mock()

    def test_delete(self):
        pk = self.maturity.pk
        self.maturity.delete()
        self.mocked_update_cache.assert_called_once_with(
            'Maturity', pk, self.maturity)

    def test_delete_delayed(self):
        self.maturity._delay_cache = True
        self.maturity.delete()
        self.mocked_update_cache.assert_not_called()


class TestSaveSignal(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch(
            'webplatformcompat.signals.update_cache_for_instance')
        self.mocked_update_cache = self.patcher.start()
        self.browser = Browser(id=666)

    def tearDown(self):
        self.patcher.stop()

    def test_raw(self):
        post_save_update_cache(Browser, self.browser, created=True, raw=True)
        self.mocked_update_cache.assert_not_called()

    def test_create(self):
        post_save_update_cache(Browser, self.browser, created=True, raw=False)
        self.mocked_update_cache.assert_called_once_with(
            'Browser', 666, self.browser)

    def test_create_delayed(self):
        self.browser._delay_cache = True
        post_save_update_cache(Browser, self.browser, created=True, raw=False)
        self.mocked_update_cache.assert_not_called()
