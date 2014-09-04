# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet as BaseModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet as BaseROModelViewSet
from rest_framework_json_api.parsers import JsonApiParser

from .mixins import PartialPutMixin
from .models import Browser, BrowserVersion
from .renderers import JsonApiRenderer
from .serializers import (
    BrowserSerializer, BrowserVersionSerializer,
    HistoricalBrowserSerializer, HistoricalBrowserVersionSerializer,
    UserSerializer)


#
# Base classes
#

class ModelViewSet(PartialPutMixin, BaseModelViewSet):
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)
    parser_classes = (JsonApiParser, FormParser, MultiPartParser)


class ReadOnlyModelViewSet(BaseROModelViewSet):
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)


#
# 'Regular' viewsets
#

class BrowserViewSet(ModelViewSet):
    model = Browser
    serializer_class = BrowserSerializer
    filter_fields = ('slug',)


class BrowserVersionViewSet(ModelViewSet):
    model = BrowserVersion
    serializer_class = BrowserVersionSerializer
    filter_fields = ('browser', 'browser__slug', 'version', 'status')


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    filter_fields = ('username',)


#
# Historical object viewsets
#

class HistoricalBrowserViewSet(ReadOnlyModelViewSet):
    model = Browser.history.model
    serializer_class = HistoricalBrowserSerializer
    filter_fields = ('id', 'slug')


class HistoricalBrowserVersionViewSet(ReadOnlyModelViewSet):
    model = BrowserVersion.history.model
    serializer_class = HistoricalBrowserVersionSerializer
    filter_fields = ('id',)
