#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for `web-platform-compat` validators module.
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from webplatformcompat.validators import (
    LanguageDictValidator, SecureURLValidator)


class TestLanguageDictValidator(TestCase):

    def test_success(self):
        LanguageDictValidator()({'en': 'English'})

    def test_string_fails(self):
        self.assertRaises(ValidationError, LanguageDictValidator(), 'en')

    def test_list_fails(self):
        self.assertRaises(ValidationError, LanguageDictValidator(), ['en'])

    def test_no_en_fails(self):
        val = {'es': 'Espanol'}
        self.assertRaises(ValidationError, LanguageDictValidator(), val)

    def test_int_value_fails(self):
        val = {'en': 1337}
        self.assertRaises(ValidationError, LanguageDictValidator(), val)


class TestSecureURLValidator(TestCase):

    def test_success(self):
        SecureURLValidator()('https://www.example.com')

    def test_http_fails(self):
        validator = SecureURLValidator()
        self.assertRaises(ValidationError, validator, 'http://www.example.com')
