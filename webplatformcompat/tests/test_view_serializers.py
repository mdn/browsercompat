# -*- coding: utf-8 -*-
"""Tests for view serializers."""
from __future__ import unicode_literals

from django.test.utils import override_settings
from drf_cached_instances.models import CachedQueryset
from rest_framework.test import APIRequestFactory
from rest_framework.versioning import NamespaceVersioning

from webplatformcompat.cache import Cache
from webplatformcompat.history import Changeset, HistoricalRecords
from webplatformcompat.models import (
    Browser, Feature, Maturity, Reference, Section, Specification, Support,
    Version)
from webplatformcompat.view_serializers import (
    ViewFeatureSerializer, ViewFeatureExtraSerializer,
    ViewFeatureListSerializer)

from .base import TestCase


class TestBaseViewFeatureViewSet(TestCase):
    """Test /view_features/<feature_id>."""

    baseUrl = 'http://testserver'
    __test__ = False  # Don't test outside of versioned API

    def make_context(self, url, **kwargs):
        """Create a context similar to a view."""
        request = APIRequestFactory().get(url)
        request.version = self.namespace
        request.versioning_scheme = NamespaceVersioning()
        context = {'request': request}
        context.update(**kwargs)
        return context

    def test_list_representation(self):
        feature = self.create(Feature, slug='feature')
        queryset = Feature.objects.all()
        url = self.api_reverse('viewfeatures-list')
        serializer = ViewFeatureListSerializer(
            queryset, many=True, context=self.make_context(url))
        representation = serializer.to_representation(queryset)
        self.assertEqual(len(representation), 1)
        detail_url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        self.assertEqual(representation[0]['href'], self.baseUrl + detail_url)

    def setup_minimal(self):
        feature = self.create(Feature, slug='feature')
        browser = self.create(
            Browser, slug='chrome_desktop', name={'en': 'Browser'})
        version = self.create(Version, browser=browser, status='current')
        support = self.create(Support, version=version, feature=feature)
        maturity = self.create(
            Maturity, slug='maturity', name={'en': 'Maturity'})
        specification = self.create(
            Specification, maturity=maturity, slug='spec',
            name={'en': 'Specification'})
        section = self.create(Section, specification=specification)
        reference = self.create(
            Reference, feature=feature, section=section)
        feature.sections = [section]
        self.changeset.closed = True
        self.changeset.save()
        feature = Feature.objects.get(id=feature.id)  # Clear cached properties
        return {
            'feature': feature,
            'browser': browser,
            'version': version,
            'support': support,
            'maturity': maturity,
            'specification': specification,
            'section': section,
            'reference': reference,
        }

    def test_minimal(self):
        """Get a minimal but complete viewfeature."""
        resources = self.setup_minimal()
        browser = resources['browser']
        feature = resources['feature']
        reference = resources['reference']
        section = resources['section']
        support = resources['support']
        maturity = resources['maturity']
        version = resources['version']
        specification = resources['specification']
        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        serializer = ViewFeatureSerializer(context=self.make_context(url))
        representation = serializer.to_representation(feature)
        expected_representation = {
            'id': feature.id,
            'mdn_uri': None,
            'slug': 'feature',
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': None,
            'references': [reference.pk],
            'supports': [support.pk],
            'parent': None,
            'children': [],
            'history_current': self.history_pk(feature),
            'history': self.history_pks(feature),
            '_view_extra': {
                'browsers': [{
                    'id': browser.pk,
                    'slug': 'chrome_desktop',
                    'name': {'en': 'Browser'},
                    'note': None,
                    'history_current': self.history_pk(browser),
                    'history': self.history_pks(browser),
                }],
                'features': [],
                'maturities': [{
                    'id': maturity.id,
                    'slug': 'maturity',
                    'name': {'en': 'Maturity'},
                    'history_current': self.history_pk(maturity),
                    'history': self.history_pks(maturity),
                }],
                'references': [{
                    'id': reference.id,
                    'note': None,
                    'feature': feature.id,
                    'section': section.id,
                    'history_current': self.history_pk(reference),
                    'history': self.history_pks(reference),
                }],
                'sections': [{
                    'id': section.id,
                    'number': None,
                    'name': None,
                    'subpath': None,
                    'specification': specification.id,
                    'history_current': self.history_pk(section),
                    'history': self.history_pks(section),
                }],
                'specifications': [{
                    'id': specification.id,
                    'slug': 'spec',
                    'mdn_key': None,
                    'name': {'en': 'Specification'},
                    'uri': None,
                    'maturity': maturity.id,
                    'history_current': self.history_pk(specification),
                    'history': self.history_pks(specification),
                }],
                'supports': [{
                    'id': support.id,
                    'support': 'yes',
                    'prefix': None,
                    'prefix_mandatory': False,
                    'alternate_name': None,
                    'alternate_mandatory': False,
                    'requires_config': None,
                    'default_config': None,
                    'protected': False,
                    'note': None,
                    'version': version.id,
                    'feature': feature.id,
                    'history_current': self.history_pk(support),
                    'history': self.history_pks(support),
                }],
                'versions': [{
                    'id': version.id,
                    'version': None,
                    'release_day': None,
                    'retirement_day': None,
                    'status': 'current',
                    'release_notes_uri': None,
                    'note': None,
                    'order': 0,
                    'browser': browser.id,
                    'history_current': self.history_pk(version),
                    'history': self.history_pks(version),
                }],
                'meta': {
                    'compat_table': {
                        'tabs': [
                            {
                                'name': {'en': 'Desktop Browsers'},
                                'browsers': [str(browser.pk)]
                            },
                        ],
                        'supports': {
                            str(feature.pk): {
                                str(browser.pk): [str(support.pk)],
                            }
                        },
                        'child_pages': False,
                        'pagination': {
                            'linked.features': {
                                'previous': None,
                                'next': None,
                                'count': 0,
                            },
                        },
                        'languages': ['en'],
                        'notes': {},
                    }
                }
            }
        }
        self.assertDataEqual(representation, expected_representation)

    def test_canonical_removed(self):
        """zxx (non-linguistic, canonical) does not appear in languages."""
        resources = self.setup_minimal()
        feature = resources['feature']
        del self.changeset
        self.create(
            Feature, parent=feature, slug='child', name='{"zxx": "canonical"}')
        self.changeset.closed = True
        self.changeset.save()
        feature = Feature.objects.get(pk=feature.pk)
        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        serializer = ViewFeatureSerializer(context=self.make_context(url))
        representation = serializer.to_representation(feature)
        compat_table = representation['_view_extra']['meta']['compat_table']
        self.assertEqual(compat_table['languages'], ['en'])

    def test_multiple_versions(self):
        """Meta section spells out significant versions."""
        feature = self.create(Feature, slug='feature')
        browser = self.create(Browser, slug='browser', name={'en': 'Browser'})
        version1 = self.create(
            Version, browser=browser, status='current', version='1.0')
        version2 = self.create(
            Version, browser=browser, status='current', version='2.0')
        version3 = self.create(
            Version, browser=browser, status='current', version='3.0')
        support1 = self.create(
            Support, version=version1, feature=feature, support='no')
        # No change in support
        self.create(
            Support, version=version2, feature=feature, support='no')
        support3 = self.create(
            Support, version=version3, feature=feature, support='yes')
        self.changeset.closed = True
        self.changeset.save()

        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        serializer = ViewFeatureSerializer(context=self.make_context(url))
        representation = serializer.to_representation(feature)
        compat_table = representation['_view_extra']['meta']['compat_table']
        expected_supports = {
            str(feature.pk): {
                str(browser.pk): [str(support1.pk), str(support3.pk)],
            }
        }
        self.assertEqual(compat_table['supports'], expected_supports)

    def setup_feature_tree(self):
        feature = self.create(Feature, slug='feature')
        for count in range(3):
            self.create(Feature, slug='child%d' % count, parent=feature)
        self.changeset.closed = True
        self.changeset.save()
        feature = Feature.objects.get(id=feature.id)  # Clear cached properties
        return feature

    @override_settings(PAGINATE_VIEW_FEATURE=2)
    def test_large_feature_tree(self):
        feature = self.setup_feature_tree()
        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        context = self.make_context(url, include_child_pages=True)
        serializer = ViewFeatureSerializer(context=context)
        representation = serializer.to_representation(feature)
        next_page = url + '?child_pages=1&page=2'
        expected_pagination = {
            'linked.features': {
                'previous': None,
                'next': self.baseUrl + next_page,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertDataEqual(expected_pagination, actual_pagination)

        context2 = self.make_context(next_page, include_child_pages=True)
        serializer2 = ViewFeatureSerializer(context=context2)
        representation = serializer2.to_representation(feature)
        expected_pagination = {
            'linked.features': {
                'previous': self.baseUrl + url + '?child_pages=1&page=1',
                'next': None,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertEqual(expected_pagination, actual_pagination)

    @override_settings(PAGINATE_VIEW_FEATURE=2)
    def test_large_feature_tree_cached_feature(self):
        feature = self.setup_feature_tree()
        cached_qs = CachedQueryset(
            Cache(), Feature.objects.all(), primary_keys=[feature.pk])
        cached_feature = cached_qs.get(pk=feature.pk)
        self.assertEqual(cached_feature.pk, feature.id)
        self.assertEqual(cached_feature.descendant_count, 3)
        self.assertEqual(cached_feature.descendant_pks, [])  # Too big to cache

        url = self.api_reverse('viewfeatures-detail', pk=cached_feature.pk)
        context = self.make_context(url, include_child_pages=True)
        serializer = ViewFeatureSerializer(context=context)
        representation = serializer.to_representation(cached_feature)
        next_page = url + '?child_pages=1&page=2'
        expected_pagination = {
            'linked.features': {
                'previous': None,
                'next': self.baseUrl + next_page,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertDataEqual(expected_pagination, actual_pagination)

        context2 = self.make_context(next_page, include_child_pages=True)
        serializer2 = ViewFeatureSerializer(context=context2)
        representation = serializer2.to_representation(feature)
        expected_pagination = {
            'linked.features': {
                'previous': self.baseUrl + url + '?child_pages=1&page=1',
                'next': None,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertEqual(expected_pagination, actual_pagination)

    @override_settings(PAGINATE_VIEW_FEATURE=2)
    def test_large_feature_tree_html(self):
        feature = self.setup_feature_tree()
        url = self.api_reverse(
            'viewfeatures-detail', pk=feature.pk, format='html')
        context = self.make_context(
            url, include_child_pages=True, format='html')
        serializer = ViewFeatureSerializer(context=context)
        representation = serializer.to_representation(feature)
        next_url = self.baseUrl + url + '?child_pages=1&page=2'
        expected_pagination = {
            'linked.features': {
                'previous': None,
                'next': next_url,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertEqual(expected_pagination, actual_pagination)
        self.assertTrue('.html' in next_url)

    @override_settings(PAGINATE_VIEW_FEATURE=4)
    def test_just_right_feature_tree(self):
        feature = self.setup_feature_tree()
        self.assertEqual(feature.descendant_count, 3)
        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        context = self.make_context(url, include_child_pages=True)
        serializer = ViewFeatureSerializer(context=context)
        representation = serializer.to_representation(feature)
        expected_pagination = {
            'linked.features': {
                'previous': None,
                'next': None,
                'count': 3,
            }
        }
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_pagination = compat_table['pagination']
        self.assertDataEqual(expected_pagination, actual_pagination)

    def test_important_versions(self):
        feature = self.create(Feature, slug='feature')
        browser = self.create(Browser, slug='browser')
        v1 = self.create(Version, browser=browser, version='1')
        support = {
            'support': 'yes',
            'prefix': '--pre',
            'prefix_mandatory': True,
            'alternate_name': 'future',
            'alternate_mandatory': True,
            'requires_config': 'feature=Yes',
            'default_config': 'feature=No',
            'protected': False,
            'note': {'en': 'note'},
        }
        s1 = self.create(Support, version=v1, feature=feature, **support)

        v2 = self.create(Version, browser=browser, version='2')
        support['prefix_mandatory'] = False
        s2 = self.create(Support, version=v2, feature=feature, **support)

        v3 = self.create(Version, browser=browser, version='3')
        support['prefix'] = ''
        s3 = self.create(Support, version=v3, feature=feature, **support)

        v4 = self.create(Version, browser=browser, version='4')
        support['alternate_mandatory'] = False
        s4 = self.create(Support, version=v4, feature=feature, **support)

        v5 = self.create(Version, browser=browser, version='5')
        support['alternate_name'] = ''
        s5 = self.create(Support, version=v5, feature=feature, **support)

        # BORING VERSION
        v51 = self.create(Version, browser=browser, version='5.1')
        self.create(Support, version=v51, feature=feature, **support)

        v6 = self.create(Version, browser=browser, version='6')
        support['default_config'] = 'feature=Yes'
        s6 = self.create(Support, version=v6, feature=feature, **support)

        v7 = self.create(Version, browser=browser, version='7')
        support['protected'] = True
        s7 = self.create(Support, version=v7, feature=feature, **support)

        v8 = self.create(Version, browser=browser, version='8')
        support['note']['es'] = 'el note'
        s8 = self.create(Support, version=v8, feature=feature, **support)

        v9 = self.create(Version, browser=browser, version='9')
        support['note'] = None
        s9 = self.create(Support, version=v9, feature=feature, **support)

        url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        context = self.make_context(url)
        serializer = ViewFeatureSerializer(context=context)
        representation = serializer.to_representation(feature)
        expected_supports = {
            str(feature.pk): {
                str(browser.pk): [
                    str(s1.pk), str(s2.pk), str(s3.pk), str(s4.pk),
                    str(s5.pk), str(s6.pk), str(s7.pk), str(s8.pk),
                    str(s9.pk)
                ]}}
        compat_table = representation['_view_extra']['meta']['compat_table']
        actual_supports = compat_table['supports']
        self.assertDataEqual(expected_supports, actual_supports)


class TestBaseViewFeatureUpdates(TestCase):
    """Test updating via ViewFeatureSerializer."""

    longMessage = True
    __test__ = False  # Don't test outside of versioned API

    def setUp(self):
        self.feature = self.create(
            Feature, slug='feature', name={'en': 'Feature'})
        self.browser = self.create(
            Browser, slug='browser', name={'en': 'Browser'})
        self.version = self.create(
            Version, browser=self.browser, version='1.0',
            release_day='2015-02-17')
        self.maturity = self.create(Maturity, slug='M', name={'en': 'Mature'})
        self.spec = self.create(
            Specification, slug='spec', mdn_key='SPEC', name={'en': 'Spec'},
            uri={'en': 'http://example.com/Spec'}, maturity=self.maturity)

        self.browser_data = {
            'id': str(self.browser.id), 'slug': self.browser.slug,
            'name': self.browser.name, 'note': None,
            'versions': [self.version.id]}
        self.version_data = {
            'id': str(self.version.id), 'version': self.version.version,
            'release_day': '2015-02-17', 'retirement_day': None, 'note': None,
            'status': 'unknown', 'release_notes_uri': None,
            'browser': self.browser.id}
        self.maturity_data = {
            'id': str(self.maturity.id), 'slug': self.maturity.slug,
            'name': self.maturity.name}
        self.spec_data = {
            'id': str(self.spec.id), 'slug': self.spec.slug,
            'mdn_key': self.spec.mdn_key, 'name': self.spec.name,
            'uri': self.spec.uri,
            'maturity': self.maturity.id, 'sections': []}
        self.url = self.api_reverse('viewfeatures-detail', pk=self.feature.pk)
        request = APIRequestFactory().get(self.url)
        request.version = self.namespace
        request.versioning_scheme = NamespaceVersioning()
        request.user = self.user
        self.context = {'request': request}
        HistoricalRecords.thread.request = request

    def assertUpdateSuccess(self, data):
        feature = Feature.objects.get(id=self.feature.id)  # Clear prop caches
        serializer = ViewFeatureSerializer(
            feature, data=data, context=self.context, partial=True)
        self.assertTrue(serializer.is_valid())
        return serializer.save()

    def assertUpdateFailed(self, data, expected_errors):
        feature = Feature.objects.get(id=self.feature.id)  # Clear prop caches
        serializer = ViewFeatureSerializer(
            feature, data=data, context=self.context, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, expected_errors)

    def test_just_feature(self):
        data = {
            'mdn_uri': {
                'en': 'https://developer.mozilla.org/en-US/docs/feature',
                'fr': 'https://developer.mozilla.org/fr/docs/feature',
            },
            'name': {
                'en': 'The Feature',
                'fr': 'Le Feature',
            }
        }
        new_feature = self.assertUpdateSuccess(data)
        self.assertEqual(new_feature.mdn_uri, data['mdn_uri'])
        self.assertEqual(new_feature.name, data['name'])

    def test_add_subfeature(self):
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'subfeature',
                    'name': {'en': 'Sub Feature'},
                    'parent': self.feature.pk,
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        subfeature = Feature.objects.get(slug='subfeature')
        self.assertEqual(subfeature.parent, new_feature)
        self.assertEqual(list(new_feature.children.all()), [subfeature])
        self.assertEqual(list(new_feature.get_descendants()), [subfeature])

    def test_add_second_subfeature(self):
        sf1 = self.create(
            Feature, slug='sf1', name={'en': 'sf1'}, parent=self.feature)
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_sf2',
                    'slug': 'sf2',
                    'name': {'en': 'Sub Feature 2'},
                    'parent': self.feature.pk,
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        sf2 = Feature.objects.get(slug='sf2')
        self.assertEqual(sf2.parent, new_feature)
        self.assertEqual(list(new_feature.children.all()), [sf1, sf2])

    def test_add_second_subfeature_with_existing_support(self):
        detail1 = self.create(
            Feature, slug='detail1', name={'en': 'Detail 1'},
            parent=self.feature)
        self.create(Support, version=self.version, feature=detail1)
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_detail2',
                    'slug': 'detail2',
                    'name': {'en': 'Detail 2'},
                    'parent': self.feature.pk
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        detail2 = Feature.objects.get(slug='detail2')
        self.assertEqual(detail2.parent, new_feature)
        self.assertEqual(list(new_feature.children.all()), [detail1, detail2])

    def test_update_existing_subfeature(self):
        subfeature = self.create(
            Feature, slug='subfeature', name={'en': 'subfeature'},
            parent=self.feature)
        data = {
            'children': [subfeature.pk],
            '_view_extra': {
                'features': [{
                    'id': subfeature.id,
                    'slug': 'subfeature',
                    'name': {'en': 'subfeature 1'},
                    'parent': self.feature.pk,
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        new_subfeature = Feature.objects.get(id=subfeature.id)
        self.assertEqual(new_subfeature.parent, self.feature)
        self.assertEqual(new_subfeature.name, {'en': 'subfeature 1'})
        self.assertEqual(list(new_feature.children.all()), [new_subfeature])

    def test_add_subsupport(self):
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'subfeature',
                    'name': {'en': 'Sub Feature'},
                    'parent': self.feature.pk,
                }],
                'supports': [{
                    'id': '_new_yes',
                    'support': 'yes',
                    'version': self.version.id,
                    'feature': '_new',
                }],
                'browsers': [self.browser_data],
                'versions': [self.version_data],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        subfeature = Feature.objects.get(slug='subfeature')
        self.assertEqual(subfeature.parent, new_feature)
        self.assertEqual(subfeature.name, {'en': 'Sub Feature'})
        supports = subfeature.supports.all()
        self.assertEqual(1, len(supports))
        support = supports[0]
        self.assertEqual(support.version, self.version)
        self.assertEqual('yes', support.support)

    def test_no_change_no_id(self):
        subfeature = self.create(
            Feature, slug='subfeature', name={'en': 'subfeature'},
            parent=self.feature)
        history_count = subfeature.history.all().count()
        data = {
            '_view_extra': {
                'features': [{
                    'slug': 'subfeature',
                    'mdn_uri': None,
                    'experimental': False,
                    'standardized': True,
                    'stable': True,
                    'obsolete': False,
                    'name': {'en': 'subfeature'},
                    'parent': self.feature.id,
                    'references': [],
                    'children': [],
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        subfeature = Feature.objects.get(slug='subfeature')
        self.assertEqual(subfeature.parent, new_feature)
        self.assertEqual(subfeature.name, {'en': 'subfeature'})
        self.assertEqual(history_count, subfeature.history.all().count())

    def test_changeset_is_applied_to_items(self):
        changeset = self.create(Changeset, closed=False, user=self.user)
        self.context['request'].changeset = changeset
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'subfeature',
                    'name': {'en': 'Sub Feature'},
                    'parent': self.feature.pk,
                }],
            },
        }
        new_feature = self.assertUpdateSuccess(data)
        subfeature = Feature.objects.get(slug='subfeature')
        self.assertEqual(subfeature.parent, new_feature)
        self.assertEqual(
            changeset.id,
            subfeature.history.last().history_changeset_id)
        changeset.closed = True
        changeset.save()

    def test_invalid_subfeature(self):
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': None,
                    'name': {'en': 'Sub Feature'},
                    'parent': self.feature.pk,
                }],
            },
        }
        expected_errors = {
            '_view_extra': {
                'features': {
                    0: {
                        'slug': ['This field may not be null.'],
                    },
                },
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_invalid_support(self):
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'subfeature',
                    'name': {'en': 'Sub Feature'},
                    'parent': self.feature.pk,
                }],
                'supports': [{
                    'id': '_new_maybe',
                    'support': 'maybe',
                    'version': self.version.id,
                    'feature': '_new',
                }],
                'browsers': [self.browser_data],
                'versions': [self.version_data],
            },
        }
        expected_errors = {
            '_view_extra': {
                'supports': {
                    0: {
                        'support': ['"maybe" is not a valid choice.'],
                    },
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_add_reference(self):
        data = {
            'references': ['_reference'],
            '_view_extra': {
                'references': [{
                    'id': '_reference',
                    'feature': self.feature.id,
                    'section': '_section',
                }],
                'sections': [{
                    'id': '_section',
                    'name': {'en': 'Section'},
                    'specification': self.spec.id,
                }],
                'specifications': [self.spec_data],
                'maturities': [self.maturity_data],
            }
        }
        new_feature = self.assertUpdateSuccess(data)
        reference = Reference.objects.get()
        self.assertEqual(new_feature, reference.feature)

    def test_add_support_to_target(self):
        data = {
            '_view_extra': {
                'supports': [{
                    'id': '_yes',
                    'support': 'yes',
                    'version': self.version.id,
                    'feature': self.feature.id,
                }],
                'versions': [self.version_data],
                'browsers': [self.browser_data],
            }
        }
        self.assertUpdateSuccess(data)
        support = Support.objects.get()
        self.assertEqual(self.version, support.version)
        self.assertEqual(self.feature, support.feature)
        self.assertEqual('yes', support.support)

    def test_to_reprepsentation_none(self):
        # This is used by the DRF browsable API
        self.assertIsNone(ViewFeatureExtraSerializer().to_representation(None))

    def test_top_level_feature_is_error(self):
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'slug',
                    'name': {'en': 'Sub Feature'},
                    'parent': None,
                }]
            }
        }
        err_msg = (
            'Feature must be a descendant of feature %s.' % self.feature.id)
        expected_errors = {
            '_view_extra': {
                'features': {
                    0: {'parent': [err_msg]},
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_other_feature_is_error(self):
        other = self.create(
            Feature, slug='other', name={'en': 'Other'})
        data = {
            '_view_extra': {
                'features': [{
                    'id': '_new',
                    'slug': 'slug',
                    'name': {'en': 'Sub Feature'},
                    'parent': other.id
                }]
            },
        }
        err_msg = (
            'Feature must be a descendant of feature %s.' % self.feature.id)
        expected_errors = {
            '_view_extra': {
                'features': {
                    0: {'parent': [err_msg]},
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_changed_maturity_is_error(self):
        maturity_data = self.maturity_data.copy()
        maturity_data['name']['en'] = 'New Maturity Name'
        data = {
            'sections': ['_section'],
            '_view_extra': {
                'sections': [{
                    'id': '_section',
                    'name': {'en': 'Section'},
                    'specification': self.spec.id,
                    'features': [self.feature.id],
                }],
                'specifications': [self.spec_data],
                'maturities': [maturity_data],
            }
        }
        err_msg = (
            'Field can not be changed from {"en": "Mature"} to'
            ' {"en": "New Maturity Name"} as part of this update. Update the'
            ' resource by itself, and try again.')
        expected_errors = {
            '_view_extra': {
                'maturities': {
                    0: {'name': [err_msg]},
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_new_specification_is_error(self):
        data = {
            'sections': ['_section'],
            '_view_extra': {
                'sections': [{
                    'id': '_section',
                    'name': {'en': 'Section'},
                    'specification': '_NEW',
                    'features': [self.feature.id],
                }],
                'specifications': [{
                    'id': '_NEW',
                    'slug': 'NEW',
                    'mdn_key': '',
                    'name': {'en': 'New Specification'},
                    'uri': {'en': 'https://example.com/new'},
                    'maturity': self.maturity.id,
                }],
                'maturities': [self.maturity_data],
            }
        }
        err_msg = (
            'Resource can not be created as part of this update. Create'
            ' first, and try again.')
        expected_errors = {
            '_view_extra': {
                'specifications': {
                    0: {'id': [err_msg]},
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_new_version_is_error(self):
        data = {
            '_view_extra': {
                'supports': [{
                    'id': '_yes',
                    'support': 'yes',
                    'version': '_NEW',
                    'feature': self.feature.id,
                }],
                'versions': [{
                    'id': '_NEW',
                    'version': '1.0',
                    'note': None,
                    'browser': self.browser.id,
                }],
                'browsers': [self.browser_data],
            }
        }
        err_msg = (
            'Resource can not be created as part of this update. Create'
            ' first, and try again.')
        expected_errors = {
            '_view_extra': {
                'versions': {
                    0: {'id': [err_msg]}
                }
            }
        }
        self.assertUpdateFailed(data, expected_errors)

    def test_unknown_resource_ignored(self):
        data = {
            'name': {'en': 'New Name'},
            '_view_extra': {
                'unknown': [{
                    'id': '_new',
                    'foo': 'bar',
                }],
            }
        }
        new_feature = self.assertUpdateSuccess(data)
        self.assertEqual(new_feature.name, {'en': 'New Name'})
