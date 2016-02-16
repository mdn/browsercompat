#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat` models module."""
import mock
import unittest

from django.core.exceptions import ValidationError

from webplatformcompat.history import Changeset
from webplatformcompat.models import (
    Browser, Feature, Maturity, Reference, Section, Specification, Support,
    Version)
from .base import TestCase


class TestManager(TestCase):
    def setUp(self):
        self.login_user()
        changeset = Changeset.objects.create(user=self.user)
        self.patcher1 = mock.patch(
            'webplatformcompat.history.HistoricalRecords'
            '.get_history_changeset')
        self.mocked_get_history_changeset = self.patcher1.start()
        self.mocked_get_history_changeset.return_value = changeset
        self.patcher2 = mock.patch(
            'webplatformcompat.signals.update_cache_for_instance')
        self.mocked_update_cache = self.patcher2.start()

    def tearDown(self):
        self.patcher2.stop()
        self.patcher1.stop()

    def test_create(self):
        browser = Browser.objects.create()
        self.mocked_update_cache.assert_called_once_with(
            'Browser', browser.id, browser)

    def test_create_delay(self):
        Browser.objects.create(_delay_cache=True)
        self.mocked_update_cache.assert_not_called()


class TestBrowser(unittest.TestCase):

    def test_str(self):
        browser = Browser(slug='browser')
        self.assertEqual('browser', str(browser))


class TestFeature(TestCase):

    def test_str(self):
        feature = Feature(slug='feature')
        self.assertEqual('feature', str(feature))

    def add_family(self):
        parent = self.create(Feature, slug='parent')
        children = [
            self.create(Feature, slug='child%d' % i, parent=parent)
            for i in range(5)]
        return parent, children

    def test_natural_child_order(self):
        parent, children = self.add_family()
        self.assertEqual(list(parent.children.all()), children)

    def test_set_children_order_same(self):
        parent, children = self.add_family()
        parent.set_children_order(children)
        self.assertEqual(list(parent.children.all()), children)

    def test_set_children_order_rotated(self):
        parent, children = self.add_family()
        new_order = children[1:] + children[:1]
        parent.set_children_order(new_order)
        self.assertEqual(list(parent.children.all()), new_order)

    def test_set_children_swap_middle(self):
        parent, children = self.add_family()
        new_order = [
            children[0], children[1], children[3], children[2], children[4]]
        parent.set_children_order(new_order)
        self.assertEqual(list(parent.children.all()), new_order)

    def test_set_children_swapped(self):
        parent, children = self.add_family()
        new_order = [
            children[1], children[0], children[3], children[2], children[4]]
        parent.set_children_order(new_order)
        self.assertEqual(list(parent.children.all()), new_order)

    def test_row_children(self):
        parent, children = self.add_family()
        self.create(
            Feature, slug='page_child', parent=parent,
            mdn_uri='{"en": "https://example.com/page"}')
        self.assertEqual(parent.row_children, children)


class TestMaturity(unittest.TestCase):
    def test_str(self):
        maturity = Maturity(slug='Draft')
        self.assertEqual('Draft', str(maturity))


class TestReference(unittest.TestCase):
    def test_str(self):
        feature = Feature(id=100)
        section = Section(id=200)
        reference = Reference(feature=feature, section=section)
        self.assertEqual(str(reference), 'feature 100 refers to section 200')


class TestSection(unittest.TestCase):
    def test_str(self):
        section = Section(name={'en': 'The Section'})
        self.assertEqual('The Section', str(section))

    def test_str_no_name(self):
        section = Section()
        self.assertEqual('<unnamed>', str(section))

    def test_str_no_english(self):
        section = Section(name={'es': 'En Section'})
        self.assertEqual('<unnamed>', str(section))


class TestSpecification(unittest.TestCase):
    def test_str(self):
        specification = Specification(slug='spec')
        self.assertEqual('spec', str(specification))


class TestSupport(unittest.TestCase):

    def test_str(self):
        browser = Browser(slug='firefox')
        version = Version(browser=browser, version=1.0)
        feature = Feature(slug='feature')
        support = Support(version=version, feature=feature)
        self.assertEqual(
            'firefox 1.0 support for feature feature is yes', str(support))


class TestVersion(TestCase):

    def test_str(self):
        browser = Browser(slug='browser')
        bv = Version(browser=browser, version='1.0')
        self.assertEqual('browser 1.0', str(bv))

    def test_clean(self):
        browser = Browser(slug='browser')
        version = Version(version='text', browser=browser)
        self.assertRaises(ValidationError, version.clean)
