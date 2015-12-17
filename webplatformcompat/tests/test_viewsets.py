# -*- coding: utf-8 -*-
"""Tests for API viewsets."""
from __future__ import unicode_literals

from django.http import Http404
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from webplatformcompat.view_serializers import (
    ViewFeatureListSerializer, ViewFeatureRowChildrenSerializer,
    ViewFeatureSerializer)
from webplatformcompat.models import Feature

from .base import APITestCase


class TestViewFeatureBaseViewset(APITestCase):
    __test__ = False  # Don't test again an unversioned API

    def setUp(self):
        self.queryset = Feature.objects.all()

    def test_serializer_for_list(self):
        self.view.action = 'list'
        serializer_cls = self.view.get_serializer_class()
        self.assertEqual(serializer_cls, ViewFeatureListSerializer)

    def test_serializer_for_child_pages(self):
        self.view.action = 'retrieve'
        url = self.api_reverse('viewfeatures-detail', pk=1)
        request = APIRequestFactory().get(url, {'child_pages': '1'})
        self.view.request = Request(request)
        serializer_cls = self.view.get_serializer_class()
        self.assertEqual(serializer_cls, ViewFeatureSerializer)

    def test_serializer_for_rows_only(self):
        self.view.action = 'retrieve'
        url = self.api_reverse('viewfeatures-detail', pk=1)
        request = APIRequestFactory().get(url, {'child_pages': '0'})
        self.view.request = Request(request)
        serializer_cls = self.view.get_serializer_class()
        self.assertEqual(serializer_cls, ViewFeatureRowChildrenSerializer)

    def test_serializer_for_updates(self):
        self.view.action = 'partial_update'
        url = self.api_reverse('viewfeatures-detail', pk=1)
        request = APIRequestFactory().get(url, {'child_pages': '1'})
        self.view.request = Request(request)
        serializer_cls = self.view.get_serializer_class()
        self.assertEqual(serializer_cls, ViewFeatureSerializer)

    def test_get_by_id(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        ret = self.view.get_object_or_404(self.queryset, pk=feature.pk)
        self.assertEqual(ret.pk, feature.pk)
        with self.assertNumQueries(0):
            self.assertEqual(ret.parent_id, parent.id)

    def test_get_by_slug(self):
        feature = self.create(Feature, slug='feature')
        ret = self.view.get_object_or_404(self.queryset, pk=feature.slug)
        self.assertEqual(ret.pk, feature.pk)
        with self.assertNumQueries(0):
            self.assertIsNone(ret.parent_id)

    def test_get_by_slug_not_found(self):
        self.assertFalse(self.queryset.filter(slug='feature').exists())
        self.assertRaises(
            Http404, self.view.get_object_or_404, self.queryset, pk='feature')

    def test_feature_found_html(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        self.create(Feature, slug='child', parent=feature)
        url = self.api_reverse(
            'viewfeatures-detail', pk=feature.pk, format='html')
        response = self.client.get(url)
        self.assertContains(response, '<h2>Browser compatibility</h2>')

    def test_feature_not_found_html(self):
        self.assertFalse(Feature.objects.filter(id=666).exists())
        url = self.api_reverse('viewfeatures-detail', pk='666') + '.html'
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual('404 Not Found', response.content.decode('utf8'))
