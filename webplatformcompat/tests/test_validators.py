#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat` validators module."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from webplatformcompat.validators import LanguageDictValidator


class SharedLanguageDictValidatorTests(object):
    def setUp(self):
        self.validator = LanguageDictValidator(
            allow_canonical=self.allow_canonical)

    def test_success(self):
        self.validator({'en': 'English'})

    def test_null_is_success(self):
        """If DRF 3.x tries None, accept as default parameter."""
        self.validator(None)

    def test_string_fails(self):
        self.assertRaises(ValidationError, self.validator, 'en')

    def test_list_fails(self):
        self.assertRaises(ValidationError, self.validator, ['en'])

    def test_no_en_fails(self):
        val = {'es': 'Espanol'}
        self.assertRaises(ValidationError, self.validator, val)

    def test_int_value_fails(self):
        val = {'en': 1337}
        self.assertRaises(ValidationError, self.validator, val)

    def test_zxx_and_en_fails(self):
        val = {'en': 'English', 'zxx': 'canonical'}
        self.assertRaises(ValidationError, self.validator, val)

    def test_eq(self):
        same = LanguageDictValidator(allow_canonical=self.allow_canonical)
        self.assertTrue(same == self.validator)
        self.assertFalse(same != self.validator)

        diff = LanguageDictValidator(allow_canonical=not self.allow_canonical)
        self.assertFalse(diff == self.validator)
        self.assertTrue(diff != self.validator)

        self.assertFalse(1 == self.validator)
        self.assertTrue(1 != self.validator)


class TestLanguageDictValidator(SharedLanguageDictValidatorTests, TestCase):
    allow_canonical = False

    def test_zxx_fails(self):
        val = {'zxx': 'display'}
        self.assertRaises(ValidationError, self.validator, val)


class TestCanonicalDictValidator(SharedLanguageDictValidatorTests, TestCase):
    allow_canonical = True

    def test_zxx_success(self):
        self.validator({'zxx': 'display'})
