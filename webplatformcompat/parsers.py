# -*- coding: utf-8 -*-
"""Parser for the API."""
from collections import OrderedDict
from json import loads

from django.conf import settings
from django.utils.six import text_type
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser as BaseJSONParser


class JSONParser(BaseJSONParser):
    dict_class = OrderedDict

    def parse(self, stream, media_type=None, parser_context=None):
        """Parse JSON-serialized data.

        Same as base JSONParser, but uses dict_class to preserve order.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return loads(data, object_pairs_hook=self.dict_class)
        except ValueError as exc:
            raise ParseError('JSON parse error - %s' % text_type(exc))
