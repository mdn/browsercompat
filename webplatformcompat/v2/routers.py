# -*- coding: utf-8 -*-
"""URL router for v2 API endpoints."""

from rest_framework.routers import Route

from ..routers import GroupedRouter
from .viewsets import (
    BrowserViewSet, FeatureViewSet, MaturityViewSet, ReferenceViewSet,
    SectionViewSet, SpecificationViewSet, SupportViewSet, VersionViewSet,
    HistoricalBrowserViewSet, HistoricalFeatureViewSet,
    HistoricalMaturityViewSet, HistoricalReferenceViewSet,
    HistoricalSectionViewSet, HistoricalSpecificationViewSet,
    HistoricalSupportViewSet, HistoricalVersionViewSet, ChangesetViewSet,
    UserViewSet, ViewFeaturesViewSet, RelatedListRoute, RelatedItemRoute)


class GroupedRelatedRouter(GroupedRouter):
    """Add related and relationships endpoints to detail endpoints."""

    related_name = '{basename}-{dashedrelated}'
    related_url = r'^{prefix}/{lookup}/{related}{trailing_slash}$'
    relationship_name = '{basename}-relationships-{dashedrelated}'
    relationship_url = (
        r'^{prefix}/{lookup}/relationships/{related}{trailing_slash}$')
    viewset_by_name = {
        'BrowserViewSet': BrowserViewSet,
        'ChangesetViewSet': ChangesetViewSet,
        'FeatureViewSet': FeatureViewSet,
        'HistoricalBrowserViewSet': HistoricalBrowserViewSet,
        'HistoricalFeatureViewSet': HistoricalFeatureViewSet,
        'HistoricalMaturityViewSet': HistoricalMaturityViewSet,
        'HistoricalReferenceViewSet': HistoricalReferenceViewSet,
        'HistoricalSectionViewSet': HistoricalSectionViewSet,
        'HistoricalSpecificationViewSet': HistoricalSpecificationViewSet,
        'HistoricalSupportViewSet': HistoricalSupportViewSet,
        'HistoricalVersionViewSet': HistoricalVersionViewSet,
        'MaturityViewSet': MaturityViewSet,
        'ReferenceViewSet': ReferenceViewSet,
        'SectionViewSet': SectionViewSet,
        'SpecificationViewSet': SpecificationViewSet,
        'SupportViewSet': SupportViewSet,
        'UserViewSet': UserViewSet,
        'VersionViewSet': VersionViewSet,
    }

    def get_routes(self, viewset):
        """Add related and relationship routes."""
        routes = super(GroupedRelatedRouter, self).get_routes(viewset)
        related_routes = getattr(viewset, 'related_routes', [])
        for route in related_routes:
            routes.append(self.related_route(route))
            routes.append(self.relationship_route(route))

        return routes

    def related_route(self, route):
        """Construct a related route."""
        name = route.name
        initkwargs = {
            'related_viewset': self.viewset_by_name[route.viewset_name],
            'suffix': 'Related',
        }
        if isinstance(route, RelatedListRoute):
            initkwargs['related_filter_name'] = route.filter_name
            handler = 'related_list'
        else:
            assert isinstance(route, RelatedItemRoute)
            initkwargs['related_id_name'] = route.id_name
            handler = 'related_item'

        return Route(
            url=self.replace_name(self.related_url, name),
            mapping={'get': handler},
            name=self.replace_name(self.related_name, name),
            initkwargs=initkwargs,
        )

    def relationship_route(self, route):
        """Contruct a relationships route."""
        name = route.name
        mapping = {
            'get': 'relationships',
            'patch': 'relationships'
        }
        initkwargs = {
            'as_relationship': name,
            'suffix': 'Related',
        }
        return Route(
            url=self.replace_name(self.relationship_url, name),
            mapping=mapping,
            name=self.replace_name(self.relationship_name, name),
            initkwargs=initkwargs,
        )

    def replace_name(self, pattern, name):
        dashed_name = name.replace('_', '-')
        return pattern.replace(
            '{related}', name).replace('{dashedrelated}', dashed_name)


router = GroupedRelatedRouter(trailing_slash=False, version='v2')

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
