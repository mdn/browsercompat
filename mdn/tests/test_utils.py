# coding: utf-8
"""Test mdn.utils."""
from __future__ import unicode_literals

from mdn.utils import join_content
from .base import TestCase


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
        joined = join_content(["Text with", "", "blank", None, "bits", "."])
        self.assertEqual(joined, "Text with blank bits.")
