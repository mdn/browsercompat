# -*- coding: utf-8 -*-
"""Tests for API renderers."""
from __future__ import unicode_literals

from django.test import RequestFactory
from rest_framework.serializers import ListSerializer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
import mock

from .base import TestCase
from webplatformcompat.v2.renderers import JsonApiV10Renderer
from webplatformcompat.serializers import (
    BrowserSerializer, FeatureSerializer, HistoricalBrowserSerializer)


class TestJsonApiV10Renderer(TestCase):
    media_type = 'application/vnd.api+json'
    base_url = 'http://testserver/api/v2/'

    def setUp(self):
        self.renderer = JsonApiV10Renderer()

    def full_api_reverse(self, name, **kwargs):
        return 'http://testserver' + self.api_reverse(name, **kwargs)

    def make_context(
            self, status_code=200, url=None, serializer=FeatureSerializer,
            as_relationship=None, method='get', override_path=None):
        response = mock.Mock(spec_set=['status_code'])
        response.status_code = status_code
        request = getattr(RequestFactory(), method)(url or '')
        renderer_context = {
            'response': response,
            'request': request,
            'fields_extra': serializer.get_fields_extra(),
            'as_relationship': as_relationship,
            'override_path': override_path,
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
        url = self.full_api_reverse('browser-list')
        context = self.make_context(url=url, serializer=BrowserSerializer)
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'data': [],
            'links': {
                'self': url,
                'next': None,
                'prev': None,
            },
            'meta': {
                'count': 0,
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
        url = self.full_api_reverse('browser-list')
        context = self.make_context(url=url, serializer=BrowserSerializer)
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'data': [
                {
                    'id': '1',
                    'type': 'browsers',
                    'attributes': {
                        'slug': 'firefox_desktop',
                        'name': {'en': 'Firefox for Desktop'},
                        'note': None,
                    },
                    'relationships': {
                        'versions': {
                            'data': [
                                {'type': 'versions', 'id': '100'},
                                {'type': 'versions', 'id': '101'},
                            ],
                        },
                        'history_current': {
                            'data': {
                                'type': 'historical_browsers', 'id': '200'
                            },
                        },
                        'history': {
                            'data': [
                                {'type': 'historical_browsers', 'id': '200'},
                            ],
                        },
                    },
                    'links': {'self': url + '/1'},
                },
                {
                    'id': '2',
                    'type': 'browsers',
                    'attributes': {
                        'slug': 'edge',
                        'name': {'en': 'Edge'},
                        'note': None,
                    },
                    'relationships': {
                        'versions': {
                            'data': [
                                {'type': 'versions', 'id': '300'},
                                {'type': 'versions', 'id': '301'},
                            ],
                        },
                        'history_current': {
                            'data': {
                                'type': 'historical_browsers', 'id': '400'
                            },
                        },
                        'history': {
                            'data': [
                                {'type': 'historical_browsers', 'id': '400'},
                            ],
                        },
                    },
                    'links': {'self': url + '/2'},
                },
            ],
            'links': {
                'self': url,
                'next': None,
                'prev': None,
            },
            'meta': {
                'count': 2,
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
        url = self.full_api_reverse('feature-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'links': {'self': url},
            'data': {
                'id': '1',
                'type': 'features',
                'attributes': {
                    'slug': 'web',
                    'mdn_uri': None,
                    'name': {'en': 'Web'},
                },
                'relationships': {
                    'parent': {
                        'data': None,
                        'links': {
                            'self': url + '/relationships/parent',
                            'related': url + '/parent',
                        }
                    },
                    'children': {
                        'data': [
                            {'type': 'features', 'id': '2'},
                            {'type': 'features', 'id': '3'},
                            {'type': 'features', 'id': '4'},
                            {'type': 'features', 'id': '5'},
                            {'type': 'features', 'id': '6'},
                            {'type': 'features', 'id': '7'},
                        ],
                        'links': {
                            'self': url + '/relationships/children',
                            'related': url + '/children',
                        }
                    },
                },
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_empty_data(self):
        output = self.renderer.render(
            None, self.media_type, self.make_context())
        self.assertEqual(output.decode('utf8'), '')

    def test_null_id(self):
        # Related items with empty relations, such as feature.parent
        # for top-level features
        data = {'id': None}
        url = self.full_api_reverse('feature-parent', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'data': None,
            'links': {'self': url}
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_no_relationships(self):
        data = ReturnDict((
            ('id', 1),
            ('slug', 'web'),
            ('mdn_uri', None),
            ('name', {'en': 'Web'}),
        ), serializer=FeatureSerializer())
        url = self.full_api_reverse('feature-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'links': {'self': url},
            'data': {
                'id': '1',
                'type': 'features',
                'attributes': {
                    'slug': 'web',
                    'mdn_uri': None,
                    'name': {'en': 'Web'},
                },
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_no_attributes(self):
        data = ReturnDict((
            ('id', 2),
            ('parent', 1),
        ), serializer=FeatureSerializer())
        url = self.full_api_reverse('feature-detail', pk=2)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'links': {'self': url},
            'data': {
                'id': '2',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {'type': 'features', 'id': '1'},
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-parent', pk=2),
                            'related': self.full_api_reverse(
                                'feature-parent', pk=2),
                        }
                    }
                }
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_with_query_string(self):
        """Test that a URL with a query string is properly handled.

        /links/self should have the query string
        /data/relationships/<relation>/links/self should not
        """
        data = ReturnDict((
            ('id', 2),
            ('parent', 1),
        ), serializer=FeatureSerializer())
        url = self.full_api_reverse('feature-detail', pk=2) + '?foo=bar'
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'links': {'self': url},
            'data': {
                'id': '2',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {'type': 'features', 'id': '1'},
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-parent', pk=2),
                            'related': self.full_api_reverse(
                                'feature-parent', pk=2),
                        }
                    }
                }
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
                    'path': '/data/relationships/children',
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
        url = self.full_api_reverse('viewfeatures-detail', pk=1)
        output = self.renderer.render(
            data, self.media_type, self.make_context(url=url))
        expected = {
            'links': {
                'self': url
            },
            'data': {
                'id': '1',
                'type': 'features',
                'attributes': {
                    'slug': 'web',
                    'mdn_uri': None,
                    'name': {'en': 'Web'},
                },
                'relationships': {
                    'parent': {
                        'data': None,
                        'links': {
                            'self': url + '/relationships/parent',
                            'related': url + '/parent'
                        }
                    },
                    'children': {
                        'data': [
                            {'type': 'features', 'id': '2'},
                            {'type': 'features', 'id': '3'},
                        ],
                        'links': {
                            'self': url + '/relationships/children',
                            'related': url + '/children'
                        }
                    },
                },
            },
            'included': [
                {
                    'id': '2',
                    'type': 'features',
                    'attributes': {
                        'slug': 'css',
                    },
                    'relationships': {
                        'parent': {
                            'data': {'type': 'features', 'id': '1'},
                        }
                    },
                    'links': {
                        'self': self.full_api_reverse('feature-detail', pk=2),
                    },
                }, {
                    'id': '3',
                    'type': 'features',
                    'attributes': {
                        'slug': 'js',
                    },
                    'relationships': {
                        'parent': {
                            'data': {'type': 'features', 'id': '1'},
                        }
                    },
                    'links': {
                        'self': self.full_api_reverse('feature-detail', pk=3),
                    },
                }
            ],
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
                'path': '/included.features.0.parent',
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
                'path': '/included.features.subject.children',
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

    def test_as_relationship_none(self):
        data = {'parent': None}
        url = self.full_api_reverse('feature-relationships-parent', pk=6)
        context = self.make_context(
            url=url, as_relationship='parent',
            override_path=self.api_reverse('feature-detail', pk=6))
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'links': {
                'self': url,
                'related': self.full_api_reverse('feature-parent', pk=6),
            },
            'data': None
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_as_relationship_to_one(self):
        data = {'parent': 1}
        url = self.full_api_reverse('feature-relationships-parent', pk=6)
        context = self.make_context(
            url=url, as_relationship='parent',
            override_path=self.api_reverse('feature-detail', pk=6))
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'links': {
                'self': url,
                'related': self.full_api_reverse('feature-parent', pk=6),
            },
            'data': {'type': 'features', 'id': '1'}
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_as_relationship_to_many_empty(self):
        data = {'children': []}
        url = self.full_api_reverse('feature-relationships-children', pk=6)
        context = self.make_context(
            url=url, as_relationship='children',
            override_path=self.api_reverse('feature-detail', pk=6))
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'links': {
                'self': url,
                'related': self.full_api_reverse('feature-children', pk=6),
            },
            'data': []
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_as_relationship_to_many(self):
        data = {'children': [7, 8, 9]}
        url = self.full_api_reverse('feature-relationships-children', pk=6)
        context = self.make_context(
            url=url, as_relationship='children',
            override_path=self.api_reverse('feature-detail', pk=6))
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'links': {
                'self': url,
                'related': self.full_api_reverse('feature-children', pk=6),
            },
            'data': [
                {'type': 'features', 'id': '7'},
                {'type': 'features', 'id': '8'},
                {'type': 'features', 'id': '9'},
            ]
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_as_relationship_from_historical_to_current(self):
        """Test viewing the current resource ID from a historical resource.

        Such as:
        /api/v2/historical_browsers/relationships/browser
        """
        data = {'object_id': '100'}
        url = self.full_api_reverse(
            'historicalbrowser-relationships-browser', pk=200)
        context = self.make_context(
            url=url, as_relationship='browser',
            serializer=HistoricalBrowserSerializer,
            override_path=self.api_reverse('historicalbrowser-detail', pk=200))
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'data': {'type': 'browsers', 'id': '100'},
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'historicalbrowser-browser', pk=200),
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_archived_representation(self):
        data = {
            'id': 1,
            'changeset': 100,
            'event': 'created',
            'date': '2014-08-25T20:50:38.868903Z',
            'object_id': 200,
            'archived_representation': {
                'id': '200',
                'name': {'en': 'A Browser'},
                'note': None,
                'slug': 'browser',
                'links': {
                    'history_current': '1',
                    'versions': [],
                },
            },
        }
        url = self.full_api_reverse('historicalbrowser-detail', pk=1)
        browser_url = self.full_api_reverse('browser-detail', pk=200)
        context = self.make_context(
            url=url, serializer=HistoricalBrowserSerializer)
        output = self.renderer.render(data, self.media_type, context)
        expected = {
            'links': {'self': url},
            'data': {
                'id': '1',
                'type': 'historical_browsers',
                'attributes': {
                    'date': '2014-08-25T20:50:38.868903Z',
                    'event': 'created',
                    'archive_data': {
                        'id': '200',
                        'type': 'browsers',
                        'attributes': {
                            'slug': 'browser',
                            'name': {'en': 'A Browser'},
                            'note': None,
                        },
                        'relationships': {
                            'history_current': {
                                'data': {
                                    'type': 'historical_browsers',
                                    'id': '1',
                                },
                            },
                            'versions': {'data': []},
                        },
                        'links': {'self': browser_url},
                    },
                },
                'relationships': {
                    'browser': {
                        'data': {'type': 'browsers', 'id': '200'},
                        'links': {
                            'self': url + '/relationships/browser',
                            'related': url + '/browser',
                        },
                    },
                    'changeset': {
                        'data': {
                            'type': 'changesets',
                            'id': '100',
                        },
                        'links': {
                            'self': url + '/relationships/changeset',
                            'related': url + '/changeset',
                        },
                    },
                },
            },
        }
        self.assertJSONEqual(output.decode('utf8'), expected)

    def test_construct_resource_uri_with_underscore(self):
        """Test constructing a URI for a resource type with an underscore.

        This happens when fetching the related historical items, such as:
        /api/v2/browsers/6/history
        """
        # The pattern for resource
        related_history = self.api_reverse('browser-history', pk='6')
        request = RequestFactory().get(related_history)
        self.renderer.request = request
        uri = self.renderer.construct_resource_uri(
            'historical_browsers', '100', {})
        expected = 'http://testserver/api/v2/historical_browsers/100'
        self.assertEqual(expected, uri)
