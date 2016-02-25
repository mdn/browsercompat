# -*- coding: utf-8 -*-
"""URL router for v1 API endpoints."""

from ..routers import GroupedRouter
from .viewsets import (
    BrowserViewSet, FeatureViewSet, MaturityViewSet, ReferenceViewSet,
    SectionViewSet, SpecificationViewSet, SupportViewSet, VersionViewSet,
    HistoricalBrowserViewSet, HistoricalFeatureViewSet,
    HistoricalMaturityViewSet, HistoricalReferenceViewSet,
    HistoricalSectionViewSet, HistoricalSpecificationViewSet,
    HistoricalSupportViewSet, HistoricalVersionViewSet, ChangesetViewSet,
    UserViewSet, ViewFeaturesViewSet)


router = GroupedRouter(trailing_slash=False, version='v1')

router.register(r'browsers', BrowserViewSet, group='resources')
router.register(r'versions', VersionViewSet, group='resources')
router.register(r'features', FeatureViewSet, group='resources')
router.register(r'supports', SupportViewSet, group='resources')
router.register(r'specifications', SpecificationViewSet, group='resources')
router.register(r'maturities', MaturityViewSet, group='resources')
router.register(r'sections', SectionViewSet, group='resources')
router.register(r'references', ReferenceViewSet, group='resources')

router.register(r'changesets', ChangesetViewSet, group='change_control')
router.register(r'users', UserViewSet, group='change_control')

router.register(
    r'historical_browsers', HistoricalBrowserViewSet, group='history')
router.register(
    r'historical_versions', HistoricalVersionViewSet, group='history')
router.register(
    r'historical_features', HistoricalFeatureViewSet, group='history')
router.register(
    r'historical_supports', HistoricalSupportViewSet, group='history')
router.register(
    r'historical_specifications', HistoricalSpecificationViewSet,
    group='history')
router.register(
    r'historical_maturities', HistoricalMaturityViewSet, group='history')
router.register(
    r'historical_sections', HistoricalSectionViewSet, group='history')
router.register(
    r'historical_references', HistoricalReferenceViewSet, group='history')

router.register(
    r'view_features', ViewFeaturesViewSet, base_name='viewfeatures',
    group='views')
