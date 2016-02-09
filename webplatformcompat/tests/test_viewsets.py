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


class TestUserBaseViewset(APITestCase):
    """Test users resource viewset."""

    __test__ = False  # Don't test against an unversioned API

    def setUp(self):
        self.me_url = self.api_reverse('user-me')

    def test_me_anonymous(self):
        response = self.client.get(self.me_url)
        self.assertIn(response.status_code, (401, 403))

    def test_me_logged_in(self):
        self.login_user()
        response = self.client.get(self.me_url)
        expected_url = self.api_reverse('user-detail', pk=self.user.pk)
        self.assertRedirects(response, expected_url)


class TestViewFeatureBaseViewset(APITestCase):
    __test__ = False  # Don't test against an unversioned API

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
        url = self.api_reverse('viewfeatures-by-slug', slug=feature.slug)
        real_url = self.api_reverse('viewfeatures-detail', pk=feature.pk)
        request = APIRequestFactory().get(url)
        ret = self.view.alternate_lookup(request, feature.slug)
        self.assertEqual(ret.status_code, 302)
        self.assertEqual(ret.url, real_url)

    def test_get_by_slug_not_found(self):
        slug = 'feature'
        url = self.api_reverse('viewfeatures-by-slug', slug=slug)
        self.assertFalse(self.queryset.filter(slug=slug).exists())
        request = APIRequestFactory().get(url)
        self.assertRaises(
            Http404, self.view.alternate_lookup, request, slug)

    def test_feature_found_html(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        self.create(Feature, slug='child', parent=feature)
        url = self.api_reverse(
            'viewfeatures-detail', pk=feature.pk, format='html')
        response = self.client.get(url)
        self.assertContains(response, '<h2>Browser compatibility</h2>')

    def test_feature_found_by_slug_html(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        self.create(Feature, slug='child', parent=feature)
        url = self.api_reverse(
            'viewfeatures-by-slug', slug=feature.slug, format='html')
        real_url = self.api_reverse(
            'viewfeatures-detail', pk=feature.pk, format='html')
        response = self.client.get(url)
        self.assertRedirects(response, real_url)

    def test_feature_not_found_html(self):
        self.assertFalse(Feature.objects.filter(id=666).exists())
        url = self.api_reverse('viewfeatures-by-slug', slug='666') + '.html'
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
