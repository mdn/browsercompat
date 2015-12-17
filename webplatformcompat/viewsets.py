# -*- coding: utf-8 -*-
"""API endpoints for CRUD operations."""

from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.http import Http404
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet as BaseModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet as BaseROModelViewSet

from drf_cached_instances.mixins import CachedViewMixin as BaseCacheViewMixin

from .cache import Cache
from .history import Changeset
from .mixins import PartialPutMixin
from .models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)
from .serializers import (
    BrowserSerializer, FeatureSerializer, MaturitySerializer,
    SectionSerializer, SpecificationSerializer, SupportSerializer,
    VersionSerializer,
    ChangesetSerializer, UserSerializer,
    HistoricalBrowserSerializer, HistoricalFeatureSerializer,
    HistoricalMaturitySerializer, HistoricalSectionSerializer,
    HistoricalSpecificationSerializer, HistoricalSupportSerializer,
    HistoricalVersionSerializer)
from .view_serializers import (
    ViewFeatureListSerializer, ViewFeatureSerializer,
    ViewFeatureRowChildrenSerializer)


#
# Base classes
#

class CachedViewMixin(BaseCacheViewMixin):
    cache_class = Cache

    def perform_create(self, serializer):
        kwargs = {}
        if getattr(self.request, 'delay_cache', False):
            kwargs['_delay_cache'] = True
        serializer.save(**kwargs)

    def perform_update(self, serializer):
        kwargs = {}
        if getattr(self.request, 'delay_cache', False):
            kwargs['_delay_cache'] = True
        serializer.save(**kwargs)

    def perform_destroy(self, instance):
        if getattr(self.request, 'delay_cache', False):
            instance._delay_cache = True
        instance.delete()


class FieldsExtraMixin(object):

    def initialize_request(self, request, *args, **kwargs):
        irequest = super(FieldsExtraMixin, self).initialize_request(
            request, *args, **kwargs)
        self.request = irequest
        irequest.parser_context['fields_extra'] = self.get_fields_extra()
        return irequest

    def get_renderer_context(self):
        context = super(FieldsExtraMixin, self).get_renderer_context()
        context['fields_extra'] = self.get_fields_extra()
        return context

    def get_fields_extra(self):
        serializer_cls = self.get_serializer_class()
        return serializer_cls.get_fields_extra()


class ModelViewSet(
        PartialPutMixin, CachedViewMixin, FieldsExtraMixin, BaseModelViewSet):
    """Base class for ViewSets supporting CRUD operations on models."""


class ReadOnlyModelViewSet(FieldsExtraMixin, BaseROModelViewSet):
    """Base class for ViewSets supporting read operations on models."""


class ReadUpdateModelViewSet(
        PartialPutMixin, CachedViewMixin, FieldsExtraMixin, UpdateModelMixin,
        BaseROModelViewSet):
    """Base class for ViewSets supporting read and update operations."""

    pass


#
# 'Regular' viewsets
#

class BrowserBaseViewSet(ModelViewSet):
    queryset = Browser.objects.order_by('id')
    serializer_class = BrowserSerializer


class FeatureBaseViewSet(ModelViewSet):
    queryset = Feature.objects.order_by('id')
    serializer_class = FeatureSerializer


class MaturityBaseViewSet(ModelViewSet):
    queryset = Maturity.objects.order_by('id')
    serializer_class = MaturitySerializer


class SectionBaseViewSet(ModelViewSet):
    queryset = Section.objects.order_by('id')
    serializer_class = SectionSerializer


class SpecificationBaseViewSet(ModelViewSet):
    queryset = Specification.objects.order_by('id')
    serializer_class = SpecificationSerializer


class SupportBaseViewSet(ModelViewSet):
    queryset = Support.objects.order_by('id')
    serializer_class = SupportSerializer


class VersionBaseViewSet(ModelViewSet):
    queryset = Version.objects.order_by('id')
    serializer_class = VersionSerializer


#
# Change control viewsets
#

class ChangesetBaseViewSet(ModelViewSet):
    queryset = Changeset.objects.order_by('id')
    serializer_class = ChangesetSerializer


class UserBaseViewSet(CachedViewMixin, ReadOnlyModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer


#
# Historical object viewsets
#

class HistoricalBrowserBaseViewSet(ReadOnlyModelViewSet):
    queryset = Browser.history.model.objects.order_by('id')
    serializer_class = HistoricalBrowserSerializer


class HistoricalFeatureBaseViewSet(ReadOnlyModelViewSet):
    queryset = Feature.history.model.objects.order_by('id')
    serializer_class = HistoricalFeatureSerializer


class HistoricalMaturityBaseViewSet(ReadOnlyModelViewSet):
    queryset = Maturity.history.model.objects.order_by('id')
    serializer_class = HistoricalMaturitySerializer


class HistoricalSectionBaseViewSet(ReadOnlyModelViewSet):
    queryset = Section.history.model.objects.order_by('id')
    serializer_class = HistoricalSectionSerializer


class HistoricalSpecificationBaseViewSet(ReadOnlyModelViewSet):
    queryset = Specification.history.model.objects.order_by('id')
    serializer_class = HistoricalSpecificationSerializer


class HistoricalSupportBaseViewSet(ReadOnlyModelViewSet):
    queryset = Support.history.model.objects.order_by('id')
    serializer_class = HistoricalSupportSerializer


class HistoricalVersionBaseViewSet(ReadOnlyModelViewSet):
    queryset = Version.history.model.objects.order_by('id')
    serializer_class = HistoricalVersionSerializer


#
# Views
#

class ViewFeaturesBaseViewSet(ReadUpdateModelViewSet):
    queryset = Feature.objects.order_by('id')

    def get_serializer_class(self):
        """Return the serializer to use based on action and query."""
        if self.action == 'list':
            return ViewFeatureListSerializer
        else:
            if self.include_child_pages:
                return ViewFeatureSerializer
            else:
                return ViewFeatureRowChildrenSerializer

    def get_serializer_context(self):
        """Add include_child_pages to context."""
        context = super(ViewFeaturesBaseViewSet, self).get_serializer_context()
        context['include_child_pages'] = self.include_child_pages
        return context

    @cached_property
    def include_child_pages(self):
        """Return True if the response should include paginated child pages.

        The default is exclude paginated child pages, and only include row
        children that detail the subject feature.  This matches the
        expectations of most writers - the table on:

        /Web/JavaScript/Reference/Global_Objects/Object

        should only include a "Basic Support" row, not the 30+ pages under
        Object, such as:

        /Web/JavaScript/Reference/Global_Objects/Object/toString

        However, if they do want a table summarizing the entire page
        heirarchy, they can add a query parameter such as:

        ?child_pages=1

        These (and variants with capital letters) are synonyms for the default
        of excluding paginated child pages:

        ?child_pages=0
        ?child_pages=false
        ?child_pages=no
        ?child_pages=NO

        and anything else will include them:

        ?child_pages
        ?child_pages=yes
        ?child_pages=Please%20let%20me%20have%20them
        """
        if self.action != 'retrieve':
            return True
        child_pages = self.request.query_params.get('child_pages', '0')
        falsy = ('0', 'false', 'no')
        return bool(child_pages.lower() not in falsy)

    def get_object_or_404(self, queryset, *filter_args, **filter_kwargs):
        """The feature can be accessed by primary key or by feature slug."""
        pk_or_slug = filter_kwargs['pk']
        try:
            pk = int(pk_or_slug)
        except ValueError:
            try:
                # parent_id is needed by the MPTT model loader,
                # including it saves a query later.
                pk = Feature.objects.only('pk', 'parent_id').get(
                    slug=pk_or_slug).pk
            except queryset.model.DoesNotExist:
                raise Http404(
                    'No %s matches the given query.' % queryset.model)
        return super(ViewFeaturesBaseViewSet, self).get_object_or_404(
            queryset, pk=pk)
