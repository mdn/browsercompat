# -*- coding: utf-8 -*-
"""Tests for JSON API RC1 parser."""
from __future__ import unicode_literals
from collections import OrderedDict
from json import dumps

from django.utils.six import BytesIO
from rest_framework.exceptions import ParseError

from .base import TestCase
from webplatformcompat.v1.parsers import JsonApiRC1Parser
from webplatformcompat.v1.viewsets import FeatureViewSet


class TestJsonApiRC1Parser(TestCase):
    def parse(self, data):
        stream = BytesIO(dumps(data).encode('utf8'))
        parser = JsonApiRC1Parser()
        view = FeatureViewSet()
        return parser.parse(stream, None, {'view': view})

    def test_simple(self):
        resource = self.parse({
            'features': {
                'id': '1',
                'slug': 'the_feature',
                'name': {'en': 'The Feature'},
                'links': {
                    'parent': None,
                    'children': ['2', '3']
                }
            }
        })
        expected = {
            'id': '1',
            'slug': 'the_feature',
            'name': {'en': 'The Feature'},
            'parent': None,
            'children': ['2', '3']
        }
        self.assertDataEqual(resource, expected)

    def test_complex(self):
        resource = self.parse({
            'features': {
                'id': '1',
                'slug': 'the_feature',
                'name': {'en': 'The Feature'},
                'links': {
                    'parent': None,
                    'children': ['2', '3']
                }
            },
            'linked': {
                'features': [
                    {
                        'id': '2',
                        'slug': 'child2',
                        'name': {'en': 'Child 2'},
                        'links': {'parent': '1'},
                    }, {
                        'id': '3',
                        'slug': 'child3',
                        'name': {'en': 'Child 3'},
                        'links': {'parent': '1'},
                    }],
            },
            'meta': {
                'foo': 'bar'
            },
            'other': {
                'ignored': 'yep'
            }
        })
        expected = {
            'id': '1',
            'slug': 'the_feature',
            'name': {'en': 'The Feature'},
            'parent': None,
            'children': ['2', '3'],
            '_view_extra': {
                'features': [
                    {
                        'id': '2',
                        'slug': 'child2',
                        'name': {'en': 'Child 2'},
                        'parent': '1',
                    }, {
                        'id': '3',
                        'slug': 'child3',
                        'name': {'en': 'Child 3'},
                        'parent': '1',
                    }],
                'meta': {'foo': 'bar'},
            }
        }
        self.assertDataEqual(resource, expected)

    def test_duplicate_attribute_in_links(self):
        data = {
            'features': OrderedDict((
                ('parent', None),
                ('links', {'parent': None}),
            ))
        }
        self.assertRaises(ParseError, self.parse, data)

    def test_duplicate_link_in_attributes(self):
        data = {
            'features': OrderedDict((
                ('links', {'parent': None}),
                ('parent', None),
            ))
        }
        self.assertRaises(ParseError, self.parse, data)

    def test_view_extra_in_attributes(self):
        data = {
            'features': {
                '_view_extra': 'foo'
            }
        }
        self.assertRaises(ParseError, self.parse, data)

    def test_view_extra_in_links(self):
        data = {
            'features': {
                'links': {
                    '_view_extra': 'foo'
                }
            }
        }
        self.assertRaises(ParseError, self.parse, data)

    def test_meta_in_linked(self):
        data = {
            'linked': {
                'meta': 'foo'
            }
        }
        self.assertRaises(ParseError, self.parse, data)
