#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat` models module."""
import mock
import unittest

from django.core.exceptions import ValidationError

from webplatformcompat.history import Changeset
from webplatformcompat.models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version,
    post_save_update_cache)
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
            'webplatformcompat.tasks.update_cache_for_instance')
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
        browser = Browser(slug="browser")
        self.assertEqual('browser', str(browser))


class TestFeature(TestCase):

    def test_str(self):
        feature = Feature(slug="feature")
        self.assertEqual('feature', str(feature))

    def add_family(self):
        parent = self.create(Feature, slug="parent")
        children = [
            self.create(Feature, slug="child%d" % i, parent=parent)
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
        maturity = Maturity(slug="Draft")
        self.assertEqual('Draft', str(maturity))


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
        feature = Feature(slug="feature")
        support = Support(version=version, feature=feature)
        self.assertEqual(
            'firefox 1.0 support for feature feature is yes', str(support))


class TestVersion(TestCase):

    def test_str(self):
        browser = Browser(slug="browser")
        bv = Version(browser=browser, version='1.0')
        self.assertEqual('browser 1.0', str(bv))

    def test_clean(self):
        browser = Browser(slug="browser")
        version = Version(version='text', browser=browser)
        self.assertRaises(ValidationError, version.clean)


class TestSaveSignal(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch(
            'webplatformcompat.tasks.update_cache_for_instance')
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


class TestM2MChangedSignal(TestCase):
    def setUp(self):
        patcher = mock.patch(
            'webplatformcompat.tasks.update_cache_for_instance')
        self.login_user()
        self.mocked_update_cache = patcher.start()
        self.addCleanup(patcher.stop)
        self.maturity = self.create(Maturity, slug='foo')
        self.specification = self.create(Specification, maturity=self.maturity)
        self.section = self.create(Section, specification=self.specification)
        self.feature = self.create(Feature)
        self.mocked_update_cache.reset_mock()

    def tearDown(self):
        self.section.delete()
        self.specification.delete()
        self.maturity.delete()
        self.feature.delete()

    def test_add_section_to_feature(self):
        self.feature.sections.add(self.section)
        self.mocked_update_cache.assert_has_calls([
            mock.call('Feature', self.feature.pk, self.feature),
            mock.call('Section', self.section.pk, self.section)])
        self.assertEqual(self.mocked_update_cache.call_count, 2)

    def test_add_section_to_feature_delayed(self):
        self.feature._delay_cache = True
        self.feature.sections.add(self.section)
        self.mocked_update_cache.assert_not_called()

    def test_add_feature_to_section(self):
        self.section.features.add(self.feature)
        self.mocked_update_cache.assert_has_calls([
            mock.call('Feature', self.feature.pk, self.feature),
            mock.call('Section', self.section.pk, self.section)])
        self.assertEqual(self.mocked_update_cache.call_count, 2)

    def test_clear_features_from_section(self):
        self.section.features.add(self.feature)
        self.mocked_update_cache.reset_mock()
        self.section.features.clear()
        self.mocked_update_cache.assert_called_once_with(
            'Section', self.section.pk, self.section)


class TestDeleteSignal(TestCase):
    def setUp(self):
        patcher = mock.patch(
            'webplatformcompat.tasks.update_cache_for_instance')
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
