#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` fields module.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from webplatformcompat.fields import OptionalCharField, TranslatedTextField


class SharedTranslatedTextFieldTests(object):
    def test_to_native_falsy(self):
        # Converting to serializable form, falsy becomes None
        self.assertIsNone(self.ttf.to_native(''))

    def test_to_native_dict(self):
        # Converting to serializable form, dicts are passed through
        data = {"key": "value"}
        self.assertEqual(data, self.ttf.to_native(data))

    def test_from_native_falsy(self):
        # Converting from serialized form, false values are None
        self.assertIsNone(self.ttf.from_native(''))

    def test_from_native_spaces(self):
        # Converting from serialized form, spaces are None
        self.assertIsNone(self.ttf.from_native('  '))

    def test_from_native_json(self):
        # Converting from serialized form, JSON becomes dict
        json_in = '{"key": "value"}'
        json_out = {"key": "value"}
        self.assertEqual(json_out, self.ttf.from_native(json_in))


class TestTranslatedTextField(SharedTranslatedTextFieldTests, TestCase):

    def setUp(self):
        self.ttf = TranslatedTextField()

    def test_to_native_canonical(self):
        # Converting to serializable form, canonical dicts become strings
        data = {"zxx": "canonical"}
        self.assertEqual(None, self.ttf.to_native(data))

    def test_from_native_string(self):
        # Converting from serialized form, string remains string, validation
        # will raise an error
        self.assertEqual("display", self.ttf.from_native('"display"'))

    def test_from_native_bad_json(self):
        # Converting from serialized form, bad JSON becomes ValidationError
        bad_json = "{'quotes': 'wrong ones'}"
        self.assertRaises(ValidationError, self.ttf.from_native, bad_json)


class TestCanonTranslatedTextField(SharedTranslatedTextFieldTests, TestCase):

    def setUp(self):
        self.ttf = TranslatedTextField(allow_canonical=True)

    def test_to_native_canonical(self):
        # Converting to serializable form, canonical dicts become strings
        data = {"zxx": "canonical"}
        self.assertEqual("canonical", self.ttf.to_native(data))

    def test_from_native_string(self):
        # Converting from serialized form, string become canonical dicts
        expected = {"zxx": "display"}
        self.assertEqual(expected, self.ttf.from_native('"display"'))

    def test_from_native_bad_json(self):
        # Converting from serialized form, bad JSON becomes canonical
        bad_json = "{'quotes': 'wrong ones'}"
        expected = {"zxx": "{'quotes': 'wrong ones'}"}
        self.assertEqual(expected, self.ttf.from_native(bad_json))


class TestOptionalCharField(TestCase):
    def setUp(self):
        self.ocf = OptionalCharField()

    def test_to_native_string(self):
        self.assertEqual('foo', self.ocf.to_native('foo'))

    def test_to_native_empty_string(self):
        self.assertEqual(None, self.ocf.to_native(''))

    def test_from_native_string(self):
        self.assertEqual('foo', self.ocf.from_native('foo'))

    def test_from_native_null(self):
        self.assertEqual('', self.ocf.from_native(None))
