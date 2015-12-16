# -*- coding: utf-8 -*-
"""Tests for API serializers."""

from webplatformcompat.models import (
    Browser, Feature, Maturity, Section, Specification, Version)
from webplatformcompat.serializers import (
    BrowserSerializer, FeatureSerializer, HistoricalFeatureSerializer,
    HistoricalMaturitySerializer, SpecificationSerializer, UserSerializer)

from .base import TestCase


class TestBrowserSerializer(TestCase):
    """Test BrowserSerializer and common historical functionality."""

    def setUp(self):
        self.browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})

    def add_versions(self):
        v1 = self.create(Version, browser=self.browser, version='1.0')
        v2 = self.create(Version, browser=self.browser, version='2.0')
        return v1, v2

    def test_set_history_current_to_old(self):
        old_history_id = self.browser.history.latest('history_date').history_id
        self.browser.name = {'en': 'Browser'}
        self.browser.save()

        data = {'history_current': old_history_id}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_browser = serializer.save()
        histories = new_browser.history.all()
        self.assertEqual(3, len(histories))
        self.assertEqual(new_browser.name, {"en": "Old Name"})

    def test_set_history_current_to_wrong_browser_fails(self):
        other_browser = self.create(
            Browser, slug='other-browser', name={'en': 'Other Browser'})
        bad_history_id = other_browser.history.all()[0].history_id

        data = {'history_current': bad_history_id}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {'history_current': ['Invalid history ID for this object']}
        self.assertEqual(serializer.errors, expected)

    def test_set_history_current_to_same(self):
        self.browser.name = {'en': 'Browser'}
        self.browser.save()
        current_history_id = self.browser.history.all()[0].history_id

        data = {'history_current': current_history_id}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_browser = serializer.save()
        new_history_id = new_browser.history.all()[0].history_id
        self.assertNotEqual(new_history_id, current_history_id)
        histories = new_browser.history.all()
        self.assertEqual(3, len(histories))

    def test_set_versions_change_order(self):
        v1, v2 = self.add_versions()
        set_order = [v2.pk, v1.pk]
        data = {'versions': set_order}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_browser = serializer.save()
        new_order = list(new_browser.versions.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)

    def test_versions_same_order(self):
        v1, v2 = self.add_versions()
        set_order = [v1.pk, v2.pk]
        data = {'versions': set_order}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_browser = serializer.save()
        new_order = list(new_browser.versions.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)


class TestFeatureSerializer(TestCase):
    """Test FeatureSerializer."""

    def setUp(self):
        self.parent = self.create(Feature, slug='parent')
        self.feature = self.create(Feature, slug='feature', parent=self.parent)
        self.child1 = self.create(Feature, slug='child1', parent=self.feature)
        self.child2 = self.create(Feature, slug='child2', parent=self.feature)

    def test_set_children_change_order(self):
        set_order = [self.child2.pk, self.child1.pk]
        data = {'children': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        actual_children = list(
            new_feature.get_children().values_list('pk', flat=True))
        self.assertEqual(actual_children, set_order)

    def test_set_children_same_order(self):
        set_order = [self.child1.pk, self.child2.pk]
        data = {'children': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        actual_children = list(
            new_feature.get_children().values_list('pk', flat=True))
        self.assertEqual(actual_children, set_order)

    def test_set_children_omit_child_fails(self):
        data = {'children': [self.child1.pk]}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {
            'children': ['All child features must be included in children.']}
        self.assertEqual(serializer.errors, expected)

    def test_set_children_add_element_fails(self):
        new_child = self.create(Feature, slug='nkotb')
        data = {'children': [self.child1.pk, self.child2.pk, new_child.pk]}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {'children': ['Set child.parent to add a child feature.']}
        self.assertEqual(serializer.errors, expected)


class TestSpecificationSerializer(TestCase):
    """Test SpecificationSerializer."""

    def setUp(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        self.spec = self.create(
            Specification, maturity=maturity, slug="css3-animations",
            mdn_key='CSS3 Animations',
            name={'en': "CSS Animations"},
            uri={'en': 'http://dev.w3.org/csswg/css-animations/'})
        self.s46 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-direction' property"},
            subpath={'en': "#animation-direction"})
        self.s45 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-iteration-count' property"},
            subpath={'en': "#animation-iteration-count"})

    def test_set_name_without_sections(self):
        data = {'name': {'en': 'CSS3 Animations'}}
        serializer = SpecificationSerializer(
            self.spec, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_spec = serializer.save()
        self.assertEqual(new_spec.name, {'en': 'CSS3 Animations'})

    def test_set_sections_to_new_order(self):
        set_order = [self.s45.pk, self.s46.pk]
        serializer = SpecificationSerializer(
            self.spec, data={'sections': set_order}, partial=True)
        self.assertTrue(serializer.is_valid())
        new_spec = serializer.save()
        new_order = list(new_spec.sections.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)

    def test_sections_same_order(self):
        set_order = [self.s46.pk, self.s45.pk]
        serializer = SpecificationSerializer(
            self.spec, data={'sections': set_order}, partial=True)
        self.assertTrue(serializer.is_valid())
        new_spec = serializer.save()
        new_order = list(new_spec.sections.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)

    def test_set_and_revert_maturity(self):
        old_maturity_id = self.spec.maturity.id
        old_history_id = self.spec.history.all()[0].history_id
        new_maturity = self.create(
            Maturity, slug='FD', name={'en': 'Final Draft'})
        serializer_set = SpecificationSerializer(
            self.spec, data={'maturity': new_maturity.id}, partial=True)
        self.assertTrue(serializer_set.is_valid())
        new_spec = serializer_set.save()
        self.assertEqual(new_spec.maturity, new_maturity)

        serializer_revert = SpecificationSerializer(
            new_spec, data={'history_current': old_history_id}, partial=True)
        self.assertTrue(serializer_revert.is_valid())
        reverted_spec = serializer_revert.save()
        self.assertEqual(reverted_spec.maturity_id, old_maturity_id)


class TestUserSerializer(TestCase):
    """Test UserSerializer."""
    def test_to_representation(self):
        user = self.login_user()
        serializer = UserSerializer()
        representation = serializer.to_representation(user)
        self.assertEqual(representation['agreement'], 0)
        self.assertEqual(representation['permissions'], ['change-resource'])


class TestHistoricalFeatureSerializer(TestCase):
    """Test HistoricalFeatureSerializer, which has archive fields."""
    def test_to_representation_no_parent(self):
        feature = self.create(
            Feature, slug="the_feature", name={"en": "The Feature"})
        history = feature.history.all()[0]
        serializer = HistoricalFeatureSerializer()
        representation = serializer.to_representation(history)
        self.assertEqual(representation['object_id'], feature.pk)
        links = representation['archived_representation']['links']
        self.assertEqual(links['sections'], [])
        self.assertEqual(links['parent'], None)

    def test_to_representation_with_parent(self):
        parent = self.create(
            Feature, slug="the_parent", name={"en": "The Parent"})
        feature = self.create(
            Feature, slug="the_feature", name={"en": "The Feature"},
            parent=parent)
        history = feature.history.all()[0]
        serializer = HistoricalFeatureSerializer()
        representation = serializer.to_representation(history)
        links = representation['archived_representation']['links']
        self.assertEqual(links['parent'], str(parent.pk))


class TestHistoricalMaturitySerializer(TestCase):
    """Test HistoricalMaturitySerializer."""
    def test_fields_extra(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        historical = maturity.history.first()
        serializer = HistoricalMaturitySerializer(instance=historical)
        expected = {
            'id': {
                'archived_resource': True,
                'link': 'self',
                'resource': 'historical_maturities'
            },
            'changeset': {
                'link': 'to_one', 'resource': 'changesets'},
            'object_id': {
                'archived_resource': True,
                'link': 'to_one',
                'name': 'maturity',
                'resource': 'maturities'
            },
            'archived_representation': {
                'archived_resource': True,
                'is_archive_of': serializer.ArchivedObject,
                'name': 'maturities',
                'resource': 'maturities'
            },
        }
        self.assertEqual(expected, serializer.get_fields_extra())
