# -*- coding: utf-8 -*-
"""v1 API viewsets for List/Search/Create/Read/Update/Delete."""

from rest_framework.parsers import FormParser, MultiPartParser

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
from .filters import UnorderedDjangoFilterBackend
from .parsers import JsonApiRC1Parser
from .renderers import JsonApiRC1Renderer, JsonApiRC1TemplateHTMLRenderer


class WritableMixin(object):
    renderer_classes = (JsonApiRC1Renderer, BrowsableAPIRenderer)
    parser_classes = (JsonApiRC1Parser, FormParser, MultiPartParser)
    filter_backends = (UnorderedDjangoFilterBackend,)


class ReadOnlyMixin(object):
    renderer_classes = (JsonApiRC1Renderer, BrowsableAPIRenderer)
    filter_backends = (UnorderedDjangoFilterBackend,)


#
# Regular viewsets
#

class BrowserViewSet(WritableMixin, BrowserBaseViewSet):
    filter_fields = ('slug',)


class FeatureViewSet(WritableMixin, FeatureBaseViewSet):
    filter_fields = ('slug', 'parent')

    def filter_queryset(self, queryset):
        qs = super(FeatureBaseViewSet, self).filter_queryset(queryset)
        if 'parent' in self.request.query_params:
            filter_value = self.request.query_params['parent']
            if not filter_value:
                qs = qs.filter(parent=None)
        return qs


class MaturityViewSet(WritableMixin, MaturityBaseViewSet):
    filter_fields = ('slug',)


class ReferenceViewSet(WritableMixin, ReferenceBaseViewSet):
    pass


class SectionViewSet(WritableMixin, SectionBaseViewSet):
    pass


class SpecificationViewSet(WritableMixin, SpecificationBaseViewSet):
    filter_fields = ('slug', 'mdn_key')


class SupportViewSet(WritableMixin, SupportBaseViewSet):
    filter_fields = ('version', 'feature')


class VersionViewSet(WritableMixin, VersionBaseViewSet):
    filter_fields = ('browser', 'browser__slug', 'version', 'status')


#
# Change control viewsets
#

class ChangesetViewSet(WritableMixin, ChangesetBaseViewSet):
    pass


class UserViewSet(ReadOnlyMixin, UserBaseViewSet):
    filter_fields = ('username',)
    namespace = 'v1'


#
# Historical object viewsets
#

class HistoricalBrowserViewSet(ReadOnlyMixin, HistoricalBrowserBaseViewSet):
    filter_fields = ('id', 'slug')


class HistoricalFeatureViewSet(ReadOnlyMixin, HistoricalFeatureBaseViewSet):
    filter_fields = ('id', 'slug')


class HistoricalMaturityViewSet(ReadOnlyMixin, HistoricalMaturityBaseViewSet):
    filter_fields = ('id', 'slug')


class HistoricalReferenceViewSet(
        ReadOnlyMixin, HistoricalReferenceBaseViewSet):
    filter_fields = ('id',)


class HistoricalSectionViewSet(ReadOnlyMixin, HistoricalSectionBaseViewSet):
    filter_fields = ('id',)


class HistoricalSpecificationViewSet(
        ReadOnlyMixin, HistoricalSpecificationBaseViewSet):
    filter_fields = ('id', 'slug', 'mdn_key')


class HistoricalSupportViewSet(ReadOnlyMixin, HistoricalSupportBaseViewSet):
    filter_fields = ('id',)


class HistoricalVersionViewSet(ReadOnlyMixin, HistoricalVersionBaseViewSet):
    filter_fields = ('id',)


#
# Views
#

class ViewFeaturesViewSet(ViewFeaturesBaseViewSet):
    parser_classes = (JsonApiRC1Parser, FormParser, MultiPartParser)
    renderer_classes = (
        JsonApiRC1Renderer, BrowsableAPIRenderer,
        JsonApiRC1TemplateHTMLRenderer)
    filter_backends = (UnorderedDjangoFilterBackend,)
    filter_fields = ('slug',)
    template_name = 'webplatformcompat/feature-basic-v1.html'
    namespace = 'v1'
