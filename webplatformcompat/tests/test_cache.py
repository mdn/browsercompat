#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat` fields module."""
from datetime import datetime
from pytz import UTC

from django.contrib.auth.models import User

from webplatformcompat.models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)
from webplatformcompat.cache import Cache

from .base import TestCase


class TestCache(TestCase):
    def setUp(self):
        self.cache = Cache()

    def test_browser_v1_serializer(self):
        browser = self.create(Browser)
        out = self.cache.browser_v1_serializer(browser)
        expected = {
            'id': browser.id,
            'slug': u'',
            'name': {},
            'note': {},
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalbrowser',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalbrowser',
                'pk': 1,
            },
            'versions:PKList': {
                'app': u'webplatformcompat',
                'model': 'version',
                'pks': [],
            },
        }
        self.assertEqual(out, expected)

    def test_browser_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.browser_v1_serializer(None))

    def test_browser_v1_loader(self):
        browser = self.create(Browser)
        with self.assertNumQueries(3):
            obj = self.cache.browser_v1_loader(browser.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.browser_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_browser_v1_loader_not_exist(self):
        self.assertFalse(Browser.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.browser_v1_loader(666))

    def test_browser_v1_invalidator(self):
        browser = self.create(Browser)
        self.assertEqual([], self.cache.browser_v1_invalidator(browser))

    def test_feature_v1_serializer(self):
        feature = self.create(
            Feature, slug='the-slug', name='{"en": "A Name"}')
        out = self.cache.feature_v1_serializer(feature)
        expected = {
            'id': feature.id,
            'slug': 'the-slug',
            'mdn_path': '',
            'experimental': False,
            'standardized': True,
            'stable': True,
            'obsolete': False,
            'name': {"en": "A Name"},
            'supports:PKList': {
                'app': u'webplatformcompat',
                'model': 'support',
                'pks': [],
            },
            'sections:PKList': {
                'app': u'webplatformcompat',
                'model': 'section',
                'pks': [],
            },
            'parent:PK': {
                'app': u'webplatformcompat',
                'model': 'feature',
                'pk': None,
            },
            'children:PKList': {
                'app': u'webplatformcompat',
                'model': 'feature',
                'pks': [],
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalfeature',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalfeature',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_feature_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.feature_v1_serializer(None))

    def test_feature_v1_loader(self):
        feature = self.create(Feature)
        with self.assertNumQueries(5):
            obj = self.cache.feature_v1_loader(feature.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.feature_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_feature_v1_loader_not_exist(self):
        self.assertFalse(Feature.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.feature_v1_loader(666))

    def test_feature_v1_invalidator_basic(self):
        feature = self.create(Feature)
        self.assertEqual([], self.cache.feature_v1_invalidator(feature))

    def test_feature_v1_invalidator_with_relation(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='child', parent=parent)
        expected = [('Feature', parent.id, False)]
        self.assertEqual(expected, self.cache.feature_v1_invalidator(feature))

    def test_maturity_v1_serializer(self):
        maturity = self.create(
            Maturity, slug='REC', name='{"en-US": "Recommendation"}')
        out = self.cache.maturity_v1_serializer(maturity)
        expected = {
            'id': maturity.id,
            'slug': 'REC',
            'name': {"en-US": "Recommendation"},
            'specifications:PKList': {
                'app': u'webplatformcompat',
                'model': 'specification',
                'pks': [],
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalmaturity',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalmaturity',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_maturity_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.maturity_v1_serializer(None))

    def test_maturity_v1_loader(self):
        maturity = self.create(Maturity)
        with self.assertNumQueries(3):
            obj = self.cache.maturity_v1_loader(maturity.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.maturity_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_maturity_v1_loader_not_exist(self):
        self.assertFalse(Maturity.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.maturity_v1_loader(666))

    def test_maturity_v1_invalidator(self):
        maturity = self.create(Maturity)
        self.assertEqual([], self.cache.maturity_v1_invalidator(maturity))

    def test_section_v1_serializer(self):
        maturity = self.create(
            Maturity, slug="REC", name={'en': 'Recommendation'})
        spec = self.create(
            Specification, slug='mathml2', mdn_key='MathML2',
            maturity=maturity,
            name='{"en": "MathML 2.0"}',
            uri='{"en": "http://www.w3.org/TR/MathML2/"}')
        section = self.create(
            Section, specification=spec,
            number={'en': '3.2.4'},
            name={'en': 'Number (mn)'},
            subpath={'en': 'chapter3.html#presm.mn'})
        out = self.cache.section_v1_serializer(section)
        expected = {
            'id': section.id,
            'number': {"en": '3.2.4'},
            'name': {"en": "Number (mn)"},
            'subpath': {'en': 'chapter3.html#presm.mn'},
            'note': {},
            'specification:PK': {
                'app': u'webplatformcompat',
                'model': 'specification',
                'pk': spec.pk,
            },
            'features:PKList': {
                'app': u'webplatformcompat',
                'model': 'feature',
                'pks': [],
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalsection',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalsection',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_section_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.section_v1_serializer(None))

    def test_section_v1_loader(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        spec = self.create(
            Specification, slug='push_api', mdn_key='Push API',
            maturity=maturity,
            name={'en': 'Push API'},
            uri={'en': (
                'https://dvcs.w3.org/hg/push/raw-file/default/index.html')}
        )
        section = self.create(
            Section, specification=spec,
            name={'en': ''}, note={'en': 'Non standard'})
        with self.assertNumQueries(3):
            obj = self.cache.section_v1_loader(section.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.section_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_section_v1_loader_not_exist(self):
        self.assertFalse(Section.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.section_v1_loader(666))

    def test_section_v1_invalidator(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        spec = self.create(
            Specification, slug='spec', mdn_key='Spec', maturity=maturity,
            name={'en': 'Spec'},
            uri={'en': 'http://example.com/spec.html'})
        section = self.create(
            Section, specification=spec,
            name={'en': 'A section'}, subpath={'en': '#section'})
        self.assertEqual(
            [('Specification', spec.pk, False)],
            self.cache.section_v1_invalidator(section))

    def test_specification_v1_serializer(self):
        maturity = self.create(
            Maturity, slug="REC", name={'en': 'Recommendation'})
        spec = self.create(
            Specification, slug="mathml2", mdn_key='MathML2',
            maturity=maturity,
            name='{"en": "MathML 2.0"}',
            uri='{"en": "http://www.w3.org/TR/MathML2/"}')
        out = self.cache.specification_v1_serializer(spec)
        expected = {
            'id': spec.id,
            'slug': 'mathml2',
            'mdn_key': 'MathML2',
            'name': {"en": "MathML 2.0"},
            'uri': {"en": "http://www.w3.org/TR/MathML2/"},
            'sections:PKList': {
                'app': u'webplatformcompat',
                'model': 'section',
                'pks': [],
            },
            'maturity:PK': {
                'app': u'webplatformcompat',
                'model': 'maturity',
                'pk': maturity.pk,
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalspecification',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalspecification',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_specification_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.specification_v1_serializer(None))

    def test_specification_v1_loader(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        spec = self.create(
            Specification, slug='push-api', maturity=maturity,
            name={'en': 'Push API'},
            uri={'en': (
                'https://dvcs.w3.org/hg/push/raw-file/default/index.html')}
        )
        with self.assertNumQueries(3):
            obj = self.cache.specification_v1_loader(spec.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.specification_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_specification_v1_loader_not_exist(self):
        self.assertFalse(Specification.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.specification_v1_loader(666))

    def test_specification_v1_invalidator(self):
        maturity = self.create(
            Maturity, slug='WD', name={'en': 'Working Draft'})
        spec = self.create(
            Specification, slug='spec', maturity=maturity,
            name={'en': 'Spec'},
            uri={'en': 'http://example.com/spec.html'})
        self.assertEqual(
            [('Maturity', 1, False)],
            self.cache.specification_v1_invalidator(spec))

    def test_support_v1_serializer(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser, version='1.0')
        feature = self.create(Feature, slug='feature')
        support = self.create(Support, version=version, feature=feature)
        out = self.cache.support_v1_serializer(support)
        expected = {
            'id': support.id,
            "support": u"yes",
            "prefix": u"",
            "prefix_mandatory": False,
            "alternate_name": u"",
            "alternate_mandatory": False,
            "requires_config": u"",
            "default_config": u"",
            "protected": False,
            "note": {},
            "footnote": {},
            'version:PK': {
                'app': u'webplatformcompat',
                'model': 'version',
                'pk': version.id,
            },
            'feature:PK': {
                'app': u'webplatformcompat',
                'model': 'feature',
                'pk': feature.id,
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalsupport',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalsupport',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_support_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.support_v1_serializer(None))

    def test_support_v1_loader(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser, version='1.0')
        feature = self.create(Feature, slug='feature')
        support = self.create(Support, version=version, feature=feature)
        with self.assertNumQueries(2):
            obj = self.cache.support_v1_loader(support.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.support_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_support_v1_loader_not_exist(self):
        self.assertFalse(Support.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.support_v1_loader(666))

    def test_support_v1_invalidator(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser, version='1.0')
        feature = self.create(Feature, slug='feature')
        support = self.create(Support, version=version, feature=feature)
        expected = [
            ('Version', version.id, True),
            ('Feature', feature.id, True),
        ]
        self.assertEqual(expected, self.cache.support_v1_invalidator(support))

    def test_version_v1_serializer(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser)
        out = self.cache.version_v1_serializer(version)
        expected = {
            'id': version.id,
            'version': u'',
            'release_day:Date': None,
            'retirement_day:Date': None,
            'status': u'unknown',
            'release_notes_uri': {},
            'note': {},
            '_order': 0,
            'browser:PK': {
                'app': u'webplatformcompat',
                'model': 'browser',
                'pk': browser.id,
            },
            'supports:PKList': {
                'app': u'webplatformcompat',
                'model': 'support',
                'pks': [],
            },
            'history:PKList': {
                'app': u'webplatformcompat',
                'model': 'historicalversion',
                'pks': [1],
            },
            'history_current:PK': {
                'app': u'webplatformcompat',
                'model': 'historicalversion',
                'pk': 1,
            },
        }
        self.assertEqual(out, expected)

    def test_version_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.version_v1_serializer(None))

    def test_version_v1_loader(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser)
        with self.assertNumQueries(3):
            obj = self.cache.version_v1_loader(version.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.version_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_version_v1_loader_not_exist(self):
        self.assertFalse(Version.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.version_v1_loader(666))

    def test_version_v1_invalidator(self):
        browser = self.create(Browser)
        version = self.create(Version, browser=browser)
        expected = [('Browser', 1, True)]
        self.assertEqual(expected, self.cache.version_v1_invalidator(version))

    def test_user_v1_serializer(self):
        user = self.create(
            User, date_joined=datetime(2014, 9, 22, 8, 14, 34, 7, UTC))
        out = self.cache.user_v1_serializer(user)
        expected = {
            'id': user.id,
            'username': '',
            'date_joined:DateTime': '1411373674.000007',
        }
        self.assertEqual(out, expected)

    def test_user_v1_serializer_empty(self):
        self.assertEqual(None, self.cache.user_v1_serializer(None))

    def test_user_v1_inactive(self):
        user = self.create(
            User, date_joined=datetime(2014, 9, 22, 8, 14, 34, 7, UTC),
            is_active=False)
        out = self.cache.user_v1_serializer(user)
        self.assertEqual(out, None)

    def test_user_v1_loader(self):
        user = self.create(User)
        with self.assertNumQueries(1):
            obj = self.cache.user_v1_loader(user.pk)
        with self.assertNumQueries(0):
            serialized = self.cache.user_v1_serializer(obj)
        self.assertTrue(serialized)

    def test_user_v1_loader_not_exist(self):
        self.assertFalse(User.objects.filter(pk=666).exists())
        self.assertIsNone(self.cache.user_v1_loader(666))

    def test_user_v1_invalidator(self):
        user = self.create(User)
        self.assertEqual([], self.cache.user_v1_invalidator(user))
