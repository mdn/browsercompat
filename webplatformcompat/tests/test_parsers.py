# -*- coding: utf-8 -*-
"""Tests for base JSON parser."""
from __future__ import unicode_literals
from collections import OrderedDict

from django.utils.six import BytesIO
from rest_framework.exceptions import ParseError

from webplatformcompat.parsers import JSONParser
from .base import TestCase


class TestJSONParser(TestCase):
    """Test the shared JSONParser class."""

    def parse(self, raw_data):
        stream = BytesIO(raw_data.encode('utf8'))
        parser = JSONParser()
        return parser.parse(stream, None, {'encoding': 'utf8'})

    def test_parse_json(self):
        raw_data = '{"foo": "bar"}'
        expected = OrderedDict((('foo', 'bar'),))
        self.assertEqual(self.parse(raw_data), expected)

    def test_parse_invalid(self):
        raw_data = 'not: json'
        self.assertRaises(ParseError, self.parse, raw_data)
