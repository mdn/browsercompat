# -*- coding: utf-8 -*-
"""Tests for API serializers."""

from django.contrib.auth import get_user_model

from webplatformcompat.models import (
    Browser, Feature, Maturity, Reference, Section, Specification, Version)
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
        self.assertEqual(new_browser.name, {'en': 'Old Name'})

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

    def test_set_current_history_to_null_fails(self):
        self.browser.name = {'en': 'Browser'}
        self.browser.save()

        data = {'history_current': None}
        serializer = BrowserSerializer(self.browser, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {'history_current': ['Invalid history ID for this object']}
        self.assertEqual(serializer.errors, expected)


class TestFeatureSerializer(TestCase):
    """Test FeatureSerializer."""

    def setUp(self):
        self.feature = self.create(Feature, slug='feature')

    def add_children(self):
        child1 = self.create(Feature, slug='child1', parent=self.feature)
        child2 = self.create(Feature, slug='child2', parent=self.feature)
        return child1, child2

    def test_set_children_change_order(self):
        child1, child2 = self.add_children()
        set_order = [child2.pk, child1.pk]
        data = {'children': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        actual_children = list(
            new_feature.get_children().values_list('pk', flat=True))
        self.assertEqual(actual_children, set_order)

    def test_set_children_same_order(self):
        child1, child2 = self.add_children()
        set_order = [child1.pk, child2.pk]
        data = {'children': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        actual_children = list(
            new_feature.get_children().values_list('pk', flat=True))
        self.assertEqual(actual_children, set_order)

    def test_set_children_omit_child_fails(self):
        child1, child2 = self.add_children()
        data = {'children': [child1.pk]}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {
            'children': ['All child features must be included in children.']}
        self.assertEqual(serializer.errors, expected)

    def test_set_children_add_element_fails(self):
        child1, child2 = self.add_children()
        new_child = self.create(Feature, slug='nkotb')
        data = {'children': [child1.pk, child2.pk, new_child.pk]}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        expected = {'children': ['Set child.parent to add a child feature.']}
        self.assertEqual(serializer.errors, expected)

    def add_references(self):
        mat1 = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        spec1 = self.create(
            Specification, maturity=mat1, slug='css3-animations',
            mdn_key='CSS3 Animations',
            name={'en': 'CSS Animations'},
            uri={'en': 'http://dev.w3.org/csswg/css-animations/'})
        section1 = self.create(
            Section, specification=spec1,
            name={'en': "The 'animation-direction' property"},
            subpath={'en': '#animation-direction'})
        ref1 = self.create(
            Reference, feature=self.feature, section=section1)
        mat2 = self.create(
            Maturity, slug='REC', name={'en': 'Recommendation'})
        spec2 = self.create(
            Specification, maturity=mat2, slug='css3-static',
            mdn_key='CSS3 Static',
            name={'en': 'CSS3 Static Features'},
            uri={'en': 'http://dev.w3.org/csswg/css-static/'})
        section2 = self.create(
            Section, specification=spec2,
            name={'en': "The 'do-not-move' property"},
            subpath={'en': '#do-not-move'})
        ref2 = self.create(
            Reference, feature=self.feature, section=section2,
            note={'en': 'This is a dumb test section.'})
        return ref1, ref2

    def test_set_references_change_order(self):
        ref1, ref2 = self.add_references()
        set_order = [ref2.pk, ref1.pk]
        data = {'references': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        new_order = list(new_feature.references.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)

    def test_versions_same_order(self):
        ref1, ref2 = self.add_references()
        set_order = [ref1.pk, ref2.pk]
        data = {'references': set_order}
        serializer = FeatureSerializer(self.feature, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        new_feature = serializer.save()
        new_order = list(new_feature.references.values_list('pk', flat=True))
        self.assertEqual(new_order, set_order)


class TestSpecificationSerializer(TestCase):
    """Test SpecificationSerializer."""

    def setUp(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        self.spec = self.create(
            Specification, maturity=maturity, slug='css3-animations',
            mdn_key='CSS3 Animations',
            name={'en': 'CSS Animations'},
            uri={'en': 'http://dev.w3.org/csswg/css-animations/'})
        self.s46 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-direction' property"},
            subpath={'en': '#animation-direction'})
        self.s45 = self.create(
            Section, specification=self.spec,
            name={'en': "The 'animation-iteration-count' property"},
            subpath={'en': '#animation-iteration-count'})

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

    def assert_representation(self, user):
        serializer = UserSerializer()
        representation = serializer.to_representation(user)
        self.assertEqual(representation['agreement'], 0)
        self.assertEqual(representation['permissions'], ['change-resource'])

    def test_to_representation_cached(self):
        """Test serialization with a cached user."""
        user = self.login_user()  # cache backend will add related fields
        self.assert_representation(user)

    def test_to_representation_uncached(self):
        """Test serialization with a Django uncached user."""
        user = self.login_user()
        user = get_user_model().objects.get(pk=user.pk)
        self.assert_representation(user)


class TestHistoricalFeatureSerializer(TestCase):
    """Test HistoricalFeatureSerializer, which has archive fields."""

    def test_to_representation_no_parent(self):
        feature = self.create(
            Feature, slug='the_feature', name={'en': 'The Feature'})
        history = feature.history.all()[0]
        serializer = HistoricalFeatureSerializer()
        representation = serializer.to_representation(history)
        self.assertEqual(representation['object_id'], feature.pk)
        links = representation['archived_representation']['links']
        self.assertEqual(links['references'], [])
        self.assertEqual(links['parent'], None)

    def test_to_representation_with_parent(self):
        parent = self.create(
            Feature, slug='the_parent', name={'en': 'The Parent'})
        feature = self.create(
            Feature, slug='the_feature', name={'en': 'The Feature'},
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
                'resource': 'historical_maturities',
                'singular': 'historical_maturity',
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
