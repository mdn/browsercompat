# -*- coding: utf-8 -*-
"""v2 API viewsets for List/Create/Read/Update/Delete/Filter."""

from collections import OrderedDict, namedtuple
import re

from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from rest_framework.exceptions import APIException
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response

from ..exceptions import InvalidQueryParam, NotImplementedQueryParam
from ..renderers import BrowsableAPIRenderer
from ..viewsets import (
    BrowserBaseViewSet, ChangesetBaseViewSet, FeatureBaseViewSet,
    HistoricalBrowserBaseViewSet, HistoricalFeatureBaseViewSet,
    HistoricalMaturityBaseViewSet, HistoricalReferenceBaseViewSet,
    HistoricalSectionBaseViewSet, HistoricalSpecificationBaseViewSet,
    HistoricalSupportBaseViewSet, HistoricalVersionBaseViewSet,
    MaturityBaseViewSet, ReferenceBaseViewSet, SectionBaseViewSet,
    SpecificationBaseViewSet, SupportBaseViewSet, UserBaseViewSet,
    VersionBaseViewSet, ViewFeaturesBaseViewSet)
from .parsers import JsonApiV10Parser
from .renderers import JsonApiV10Renderer, JsonApiV10TemplateHTMLRenderer


#
# Helper classes
#

RelatedItemRoute = namedtuple(
    'RelatedItemRoute', ('name', 'viewset_name', 'id_name'))
RelatedListRoute = namedtuple(
    'RelatedListRoute', ('name', 'viewset_name', 'filter_name'))


class RelatedActionMixin(object):
    """Add related actions used in JSON API v1.0.

    Implementing viewsets should add two properties:
    detail_url_pattern - The URL pattern name for the detail view
    related_routes - A sequence of tuples of related routes
        (RelatedListRoute and RelatedItemRoute instances)
    """

    # View parameters set in router with initkwargs
    related_viewset = None
    related_filter_name = None
    related_id_name = None
    as_relationship = None

    # View parameter set by related_list
    related_filter = None
    filter_re = re.compile('^filter\[(?P<name>[^]]*)\]$')
    reserved_param_re = re.compile('^[a-z]*$')

    # Other parameters
    reserved_param_re = re.compile('^[a-z]*$')

    def add_related_context(self, context):
        """Add related data to a context dictionary."""
        if hasattr(self, 'override_path'):
            context['override_path'] = self.override_path
        context['as_relationship'] = self.as_relationship
        return context

    def get_renderer_context(self):
        """Add flags to context for related and relationship views."""
        renderer_context = super(
            RelatedActionMixin, self).get_renderer_context()
        renderer_context = self.add_related_context(renderer_context)
        return renderer_context

    def get_parser_context(self, http_request):
        parser_context = super(
            RelatedActionMixin, self).get_parser_context(http_request)
        parser_context = self.add_related_context(parser_context)
        return parser_context

    def filter_queryset(self, queryset):
        """Apply filters from the query string and the view."""
        filter_params = self.get_filter_params()
        for name, value in filter_params.items():
            try:
                queryset = queryset.filter(**filter_params)
            except FieldError:
                raise UnknownFilterError(name)
        return queryset

    def finalize_response(self, request, response, *args, **kwargs):
        """Restore the renderer_context for related item/list views.

        When requesting a related view, DRF's finalize_response will
        override the renderer context with the main resource's context, but
        we want the related resource's context. For example, in the
        browser-version related view, the context should have fields_extra for
        Versions, not for Browsers.  This restores the context after DRF has
        overwritten it,
        """
        response = super(RelatedActionMixin, self).finalize_response(
            request, response, *args, **kwargs)
        if hasattr(response, 'related_renderer_context'):
            response.renderer_context = response.related_renderer_context
        return response

    def get_filter_params(self):
        """Gather filters from the request and view."""
        filters = {}
        request = self.request
        fields_extra = self.serializer_class.get_fields_extra()

        # Search the request's query parameters for filters
        for key, value in request.query_params.items():
            is_filter = self.filter_re.match(key)
            if is_filter:
                name = is_filter.group('name')
                field_extra = fields_extra.get(name, {})
                if value == '' and field_extra.get('link'):
                    # Treat blank link values as None
                    value = None
                filters[name] = value
            else:
                self.verify_parameter(key)

        # Apply the implicit filter for related views
        filters.update(getattr(self, 'related_filter') or {})

        return filters

    def verify_parameter(self, key):
        """Raise an error for invalid query parameters."""
        if key in ('page', 'page_size'):
            # Pagination is handled in .pagination.Pagination class
            # TOOD: bug 1243128, use page[number] and page[size]
            pass
        elif key == 'include':
            # TODO: bug 1243190, implement included resources
            raise NotImplementedQueryParam(key)
        elif key == 'fields' or key.startswith('fields['):
            # TODO: bug 1252973, implement sparse fieldsets
            raise NotImplementedQueryParam(key)
        elif key == 'sort':
            # TODO: bug 1243195, implement sorting
            raise NotImplementedQueryParam(key)
        elif self.reserved_param_re.match(key):
            raise InvalidQueryParam(key)

    def related_item(self, request, pk):
        """Return a related item, or signal that there is no related item."""
        viewset = self.related_viewset
        id_name = self.related_id_name
        obj = self.get_object()
        related_id = getattr(obj, id_name)
        if related_id is None:
            data = OrderedDict((('id', None),))
            return Response(data)

        related_view = viewset.as_view({'get': 'retrieve'})
        response = related_view(request, pk=related_id)
        response.related_renderer_context = response.renderer_context
        id_extra = response.renderer_context['fields_extra']['id']
        resource = id_extra['resource']
        pattern = id_extra.get('singular', resource[:-1]).replace('_', '')
        path = reverse('v2:%s-detail' % pattern, kwargs={'pk': related_id})
        uri = request.build_absolute_uri(path)
        response.related_renderer_context['override_path'] = uri
        return response

    def related_list(self, request, pk):
        """Return a list of related items."""
        viewset = self.related_viewset
        filter_name = self.related_filter_name
        related_view = viewset.as_view(
            {'get': 'list'}, related_filter={filter_name: pk})
        response = related_view(request)
        response.related_renderer_context = response.renderer_context
        return response

    def relationships(self, request, pk):
        """Return the IDs of related items."""
        self.override_path = reverse(
            'v2:%s' % self.detail_url_pattern, kwargs={'pk': pk})
        method = request.method
        if method == 'GET':
            return self.retrieve(request, pk)
        else:
            # TODO: Support POST and DELETE for adding/removing specific items
            # http://jsonapi.org/format/1.0/#crud-updating-to-many-relationships
            assert method == 'PATCH'
            self.add_related_context(request.parser_context)
            return self.partial_update(request, pk)


class WritableMixin(RelatedActionMixin):
    renderer_classes = (JsonApiV10Renderer, BrowsableAPIRenderer)
    parser_classes = (JsonApiV10Parser, FormParser, MultiPartParser)


class ReadOnlyMixin(RelatedActionMixin):
    renderer_classes = (JsonApiV10Renderer, BrowsableAPIRenderer)


class UnknownFilterError(APIException):
    """400 Bad Request returned when a filter is unknown."""

    status_code = HTTP_400_BAD_REQUEST

    def __init__(self, filter_name):
        """Initialize the exception with a standard error string."""
        self.detail = 'Unknown filter "%s" requested.' % filter_name


#
# Regular viewsets
#

class BrowserViewSet(WritableMixin, BrowserBaseViewSet):
    detail_url_pattern = 'browser-detail'
    related_routes = (
        RelatedListRoute('versions', 'VersionViewSet', 'browser'),
        RelatedItemRoute(
            'history_current', 'HistoricalBrowserViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalBrowserViewSet', 'id'),
    )


class FeatureViewSet(WritableMixin, FeatureBaseViewSet):
    detail_url_pattern = 'feature-detail'
    related_routes = (
        RelatedListRoute('references', 'ReferenceViewSet', 'feature'),
        RelatedListRoute('supports', 'SupportViewSet', 'feature'),
        RelatedItemRoute('parent', 'FeatureViewSet', 'parent_id'),
        RelatedListRoute('children', 'FeatureViewSet', 'parent_id'),
        RelatedItemRoute(
            'history_current', 'HistoricalFeatureViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalFeatureViewSet', 'id'),
    )


class MaturityViewSet(WritableMixin, MaturityBaseViewSet):
    detail_url_pattern = 'maturity-detail'
    related_routes = (
        RelatedListRoute('specifications', 'SpecificationViewSet', 'maturity'),
        RelatedItemRoute(
            'history_current', 'HistoricalMaturityViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalMaturityViewSet', 'id'),
    )


class ReferenceViewSet(WritableMixin, ReferenceBaseViewSet):
    detail_url_pattern = 'reference-detail'
    related_routes = (
        RelatedItemRoute('feature', 'FeatureViewSet', 'feature_id'),
        RelatedItemRoute('section', 'SectionViewSet', 'section_id'),
        RelatedItemRoute(
            'history_current', 'HistoricalReferenceViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalReferenceViewSet', 'id'),
    )


class SectionViewSet(WritableMixin, SectionBaseViewSet):
    detail_url_pattern = 'section-detail'
    related_routes = (
        RelatedItemRoute(
            'specification', 'SpecificationViewSet', 'specification_id'),
        RelatedListRoute('features', 'FeatureViewSet', 'sections'),
        RelatedListRoute('references', 'ReferenceViewSet', 'section'),
        RelatedItemRoute(
            'history_current', 'HistoricalSectionViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalSectionViewSet', 'id'),
    )


class SpecificationViewSet(WritableMixin, SpecificationBaseViewSet):
    detail_url_pattern = 'specification-detail'
    related_routes = (
        RelatedItemRoute('maturity', 'MaturityViewSet', 'maturity_id'),
        RelatedListRoute('sections', 'SectionViewSet', 'specification'),
        RelatedItemRoute(
            'history_current', 'HistoricalSpecificationViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalSpecificationViewSet', 'id'),
    )


class SupportViewSet(WritableMixin, SupportBaseViewSet):
    detail_url_pattern = 'support-detail'
    related_routes = (
        RelatedItemRoute('version', 'VersionViewSet', 'version_id'),
        RelatedItemRoute('feature', 'FeatureViewSet', 'feature_id'),
        RelatedItemRoute(
            'history_current', 'HistoricalSupportViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalSupportViewSet', 'id'),
    )


class VersionViewSet(WritableMixin, VersionBaseViewSet):
    detail_url_pattern = 'version-detail'
    related_routes = (
        RelatedItemRoute('browser', 'BrowserViewSet', 'browser_id'),
        RelatedListRoute('supports', 'SupportViewSet', 'version'),
        RelatedItemRoute(
            'history_current', 'HistoricalVersionViewSet',
            'current_history_id'),
        RelatedListRoute('history', 'HistoricalVersionViewSet', 'id'),
    )


#
# Change control viewsets
#

class ChangesetViewSet(WritableMixin, ChangesetBaseViewSet):
    detail_url_pattern = 'changeset-detail'
    related_routes = (
        RelatedItemRoute('user', 'UserViewSet', 'user_id'),
        RelatedListRoute(
            'historical_browsers', 'HistoricalBrowserViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_features', 'HistoricalFeatureViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_maturities', 'HistoricalMaturityViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_sections', 'HistoricalSectionViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_specifications', 'HistoricalSpecificationViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_supports', 'HistoricalSupportViewSet',
            'history_changeset_id'),
        RelatedListRoute(
            'historical_versions', 'HistoricalVersionViewSet',
            'history_changeset_id'),
    )


class UserViewSet(ReadOnlyMixin, UserBaseViewSet):
    detail_url_pattern = 'user-detail'
    related_routes = (
        RelatedListRoute('changesets', 'ChangesetViewSet', 'user_id'),
    )
    namespace = 'v2'


#
# Historical object viewsets
#

changeset_route = RelatedItemRoute(
    'changeset', 'ChangesetViewSet', 'history_changeset_id')


class HistoricalBrowserViewSet(
        ReadOnlyMixin, HistoricalBrowserBaseViewSet):
    detail_url_pattern = 'historicalbrowser-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('browser', 'BrowserViewSet', 'id'),
    )


class HistoricalFeatureViewSet(
        ReadOnlyMixin, HistoricalFeatureBaseViewSet):
    detail_url_pattern = 'historicalfeature-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('feature', 'FeatureViewSet', 'id'),
    )


class HistoricalMaturityViewSet(
        ReadOnlyMixin, HistoricalMaturityBaseViewSet):
    detail_url_pattern = 'historicalmaturity-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('maturity', 'MaturityViewSet', 'id'),
    )


class HistoricalReferenceViewSet(
        ReadOnlyMixin, HistoricalReferenceBaseViewSet):
    detail_url_pattern = 'historicalreference-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('reference', 'ReferenceViewSet', 'id'),
    )


class HistoricalSectionViewSet(
        ReadOnlyMixin, HistoricalSectionBaseViewSet):
    detail_url_pattern = 'historicalsection-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('section', 'SectionViewSet', 'id'),
    )


class HistoricalSpecificationViewSet(
        ReadOnlyMixin, HistoricalSpecificationBaseViewSet):
    detail_url_pattern = 'historicalspecification-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('specification', 'SpecificationViewSet', 'id'),
    )


class HistoricalSupportViewSet(
        ReadOnlyMixin, HistoricalSupportBaseViewSet):
    detail_url_pattern = 'historicalsupport-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('support', 'SupportViewSet', 'id'),
    )


class HistoricalVersionViewSet(
        ReadOnlyMixin, HistoricalVersionBaseViewSet):
    detail_url_pattern = 'historicalversion-detail'
    related_routes = (
        changeset_route,
        RelatedItemRoute('version', 'VersionViewSet', 'id'),
    )


#
# Views
#

class ViewFeaturesViewSet(ViewFeaturesBaseViewSet):
    parser_classes = (JsonApiV10Parser, FormParser, MultiPartParser)
    renderer_classes = (
        JsonApiV10Renderer, BrowsableAPIRenderer,
        JsonApiV10TemplateHTMLRenderer)
    template_name = 'webplatformcompat/feature-basic-v2.html'
    namespace = 'v2'
