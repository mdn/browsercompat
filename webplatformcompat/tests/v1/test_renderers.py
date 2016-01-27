# -*- coding: utf-8 -*-
"""Tests for API renderers."""
from __future__ import unicode_literals

from django.test import RequestFactory
from rest_framework.serializers import ListSerializer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
import mock

from .base import TestCase
from webplatformcompat.v1.renderers import JsonApiRC1Renderer
from webplatformcompat.serializers import BrowserSerializer, FeatureSerializer


class TestJsonApiRenderers(TestCase):
    media_type = 'application/vnd.api+json'
    base_url = 'http://testserver/api/v1/'

    def setUp(self):
        self.renderer = JsonApiRC1Renderer()

    def make_context(
            self, status_code=200, url=None, serializer=FeatureSerializer,
            method='get'):
        response = mock.Mock(spec_set=['status_code'])
        response.status_code = status_code
        if url:
            request = getattr(RequestFactory(), method)(url)
        else:
            request = mock.Mock(spec_set=['build_absolute_uri', 'method'])
            request.build_absolute_uri.side_effect = Exception('not called')
        renderer_context = {
            'response': response,
            'request': request,
            'fields_extra': serializer.get_fields_extra(),
        }
        return renderer_context

    def make_list(self, data_list, serializer):
        list_serializer = ListSerializer(child=serializer)
        return ReturnList(data_list, serializer=list_serializer)

    def test_paginated_empty(self):
        data = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': self.make_list([], BrowserSerializer())
        }
        output = self.renderer.render(
            data, self.media_type, self.make_context())
        expected = {
            'browsers': [],
            'meta': {
                'pagination': {
                    'browsers': {
                        'count': 0,
                        'next': None,
                        'previous': None,
                    }
                }
            }
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_paginated_populated(self):
        browser1 = {
            'id': 1,
            'slug': 'firefox_desktop',
            'name': {'en': 'Firefox for Desktop'},
            'note': None,
            'versions': [100, 101],
            'history_current': 200,
            'history': [200]
        }
        browser2 = {
            'id': 2,
            'slug': 'edge',
            'name': {'en': 'Edge'},
            'note': None,
            'versions': [300, 301],
            'history_current': 400,
            'history': [400]
        }
        results = self.make_list([browser1, browser2], BrowserSerializer())
        data = {
            'count': 2,
            'next': None,
            'previous': None,
            'results': results
        }
        url = self.api_reverse('browser-list')
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'browsers': [
                {
                    'id': '1',
                    'slug': 'firefox_desktop',
                    'name': {'en': 'Firefox for Desktop'},
                    'note': None,
                    'links': {
                        'versions': ['100', '101'],
                        'history_current': '200',
                        'history': ['200'],
                    }
                },
                {
                    'id': '2',
                    'slug': 'edge',
                    'name': {'en': 'Edge'},
                    'note': None,
                    'links': {
                        'versions': ['300', '301'],
                        'history_current': '400',
                        'history': ['400'],
                    }
                },

            ],
            'links': {
                'browsers.versions': {
                    'type': 'versions',
                    'href': self.base_url + 'versions/{browsers.versions}',
                },
                'browsers.history_current': {
                    'type': 'historical_browsers',
                    'href': (
                        self.base_url +
                        'historical_browsers/{browsers.history_current}'),
                },
                'browsers.history': {
                    'type': 'historical_browsers',
                    'href': (
                        self.base_url +
                        'historical_browsers/{browsers.history}'),
                },
            },
            'meta': {
                'pagination': {
                    'browsers': {
                        'count': 2,
                        'next': None,
                        'previous': None,
                    }
                }
            }
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_null_link(self):
        data = ReturnDict((
            ('id', 1),
            ('slug', 'web'),
            ('mdn_uri', None),
            ('name', {'en': 'Web'}),
            ('parent', None),
            ('children', [2, 3, 4, 5, 6, 7]),
        ), serializer=FeatureSerializer())
        url = self.api_reverse('feature-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'features': {
                'id': '1',
                'slug': 'web',
                'mdn_uri': None,
                'name': {'en': 'Web'},
                'links': {
                    'parent': None,
                    'children': ['2', '3', '4', '5', '6', '7']
                }
            },
            'links': {
                'features.parent': {
                    'type': 'features',
                    'href': self.base_url + 'features/{features.parent}',
                },
                'features.children': {
                    'type': 'features',
                    'href': self.base_url + 'features/{features.children}',
                },
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_empty_data(self):
        output = self.renderer.render(
            None, self.media_type, self.make_context())
        self.assertEqual(output.decode('utf8'), '')

    def test_no_links(self):
        data = ReturnDict((
            ('id', 1),
            ('slug', 'web'),
            ('mdn_uri', None),
            ('name', {'en': 'Web'}),
        ), serializer=FeatureSerializer())
        url = self.api_reverse('feature-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'features': {
                'id': '1',
                'slug': 'web',
                'mdn_uri': None,
                'name': {'en': 'Web'},
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_permission_denied(self):
        data = {
            'detail': 'You do not have permission to perform this action.'
        }
        output = self.renderer.render(
            data, self.media_type, self.make_context(status_code=403))
        expected = {
            'errors': [
                {
                    'detail': data['detail'],
                    'status': '403'
                }
            ]
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_field_validation_error(self):
        data = ReturnDict((
            ('children', ['Set child.parent to add a child feature.']),
        ), serializer=FeatureSerializer())
        output = self.renderer.render(
            data, self.media_type, self.make_context(status_code=400))
        expected = {
            'errors': [
                {
                    'detail': 'Set child.parent to add a child feature.',
                    'path': '/children',
                    'status': '400'
                }
            ]
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_view_extra(self):
        feature2 = {
            'id': 2,
            'slug': 'css',
            'parent': 1
        }
        feature3 = {
            'id': 3,
            'slug': 'js',
            'parent': 1
        }
        data = ReturnDict((
            ('id', 1),
            ('slug', 'web'),
            ('mdn_uri', None),
            ('name', {'en': 'Web'}),
            ('parent', None),
            ('children', [2, 3]),
            ('_view_extra', {
                'features': self.make_list(
                    [feature2, feature3], FeatureSerializer()),
                'meta': {'foo': 'bar'},
            }),
        ), serializer=FeatureSerializer())
        url = self.api_reverse('viewfeatures-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'features': {
                'id': '1',
                'slug': 'web',
                'mdn_uri': None,
                'name': {'en': 'Web'},
                'links': {
                    'parent': None,
                    'children': ['2', '3'],
                },
            },
            'linked': {
                'features': [
                    {
                        'id': '2',
                        'slug': 'css',
                        'links': {'parent': '1'},
                    }, {
                        'id': '3',
                        'slug': 'js',
                        'links': {'parent': '1'},
                    }
                ]
            },
            'links': {
                'features.children': {
                    'type': 'features',
                    'href': self.base_url + 'features/{features.children}',
                },
                'features.parent': {
                    'type': 'features',
                    'href': self.base_url + 'features/{features.parent}',
                },
            },
            'meta': {
                'foo': 'bar'
            }
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_linked_error(self):
        data = {
            '_view_extra': {
                'features': {
                    0: {'parent': ['Feature must be a descendant.']},
                }
            }
        }
        output = self.renderer.render(
            data, self.media_type, self.make_context(status_code=400))
        expected = {
            'errors': [{
                'status': '400',
                'path': '/linked.features.0.parent',
                'detail': 'Feature must be a descendant.'
            }]
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_subject_error(self):
        data = {
            '_view_extra': {
                'features': {
                    None: {'children': ['MYSTERY ERROR.']},
                }
            }
        }
        output = self.renderer.render(
            data, self.media_type, self.make_context(status_code=400))
        expected = {
            'errors': [{
                'status': '400',
                'path': '/linked.features.subject.children',
                'detail': 'MYSTERY ERROR.'
            }]
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_options(self):
        data = {
            'actions': {
                'PUT': {
                    # In full OPTIONS response, PUT has all field data
                    'names': {'attributues': 'values'}
                },
            },
            'description': '',
            'name': 'Browser',
            'parses': [
                'application/vnd.api+json',
                'application/x-www-form-urlencoded',
                'multipart/form-data',
            ],
            'renders': ['application/vnd.api+json', 'text/html']
        }
        url = self.api_reverse('browser-detail', pk=1)
        context = self.make_context(
            url=url, serializer=BrowserSerializer, method='options')
        output = self.renderer.render(data, self.media_type, context)
        expected = {'meta': data}
        self.assertJSONEqual(output.decode('utf8'), expected)
