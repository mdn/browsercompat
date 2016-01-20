# coding: utf-8
"""Test mdn.utils."""
from __future__ import unicode_literals
from datetime import date

from mdn.utils import (
    date_to_iso, end_of_line, format_version, is_new_id, join_content,
    slugify)
from .base import TestCase


class TestDateToIso(TestCase):
    def test_date(self):
        self.assertEqual('2015-02-02', date_to_iso(date(2015, 2, 2)))

    def test_none(self):
        self.assertEqual(None, date_to_iso(''))


class TestEndOfLine(TestCase):
    def test_single_line(self):
        line = 'This is a single line.'
        self.assertEqual(len(line), end_of_line(line, 2))

    def test_multiple_line(self):
        line = 'This is a multi line\nSee, two lines'
        self.assertEqual(20, end_of_line(line, 2))


class TestFormatVersion(TestCase):
    def test_dotted(self):
        self.assertEqual('1.0', format_version('1.0'))

    def test_double_dotted(self):
        self.assertEqual('1.0.1', format_version('1.0.1'))

    def test_plain(self):
        self.assertEqual('1.0', format_version('1'))


class TestIsNewID(TestCase):
    def test_new_id(self):
        self.assertTrue(is_new_id('_new'))

    def test_string_id(self):
        self.assertFalse(is_new_id('6'))

    def test_int_id(self):
        self.assertFalse(is_new_id(6))


class TestJoinContent(TestCase):
    def test_join_content_simple(self):
        joined = join_content(['Works', 'like', 'join.'])
        self.assertEqual(joined, 'Works like join.')

    def test_join_content_code(self):
        joined = join_content([
            'Text with', '<code>code1</code>', ',' '<code>code2</code>',
            ', and', '<code>code3</code>', 'blocks.'])
        expected_text = (
            'Text with <code>code1</code>,<code>code2</code>, and'
            ' <code>code3</code> blocks.')
        self.assertEqual(joined, expected_text)

    def test_join_content_empty(self):
        joined = join_content(['Text with', '', 'blank', None, 'bits', '.'])
        self.assertEqual(joined, 'Text with blank bits.')


class TestSlugify(TestCase):
    def test_already_slugged(self):
        self.assertEqual('foo', slugify('foo'))

    def test_long_string(self):
        self.assertEqual(
            'abcdefghijklmnopqrstuvwxyz-abcdefghijklmnopqrstuvw',
            slugify('ABCDEFGHIJKLMNOPQRSTUVWXYZ-abcdefghijklmnopqrstuvwxyz'))

    def test_non_ascii(self):
        self.assertEqual('_', slugify('Рекомендация'))

    def test_limit(self):
        self.assertEqual(
            'abcdefghij', slugify('ABCDEFGHIJKLMNOPQRSTUVWXYZ', length=10))

    def test_num_suffix(self):
        self.assertEqual('slug13', slugify('slug', suffix=13))
