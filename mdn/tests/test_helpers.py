# -*- coding: utf-8 -*-
"""Tests for jingo/jinja2 helper functions and filters."""

from __future__ import unicode_literals
from collections import OrderedDict
import mock

from django.core.paginator import Paginator
from django.test import override_settings
from django.utils.six.moves.urllib_parse import urlparse, parse_qsl

from mdn.templatetags.helpers import (
    add_filter_to_current_url, drop_filter_from_current_url, page_list,
    pagination_control, can_reparse_mdn_import)
from webplatformcompat.tests.base import TestCase as BaseTestCase


class TestCase(BaseTestCase):
    def page(self, number, total):
        paginator = Paginator(range(total * 2), 2)
        return paginator.page(number)


class TestPageList(TestCase):
    def test_empty(self):
        page = self.page(1, 0)
        self.assertEqual([1], page_list(page))

    def test_two_pages(self):
        page = self.page(1, 2)
        self.assertEqual([1, 2], page_list(page))

    def test_five_pages(self):
        page = self.page(3, 5)
        self.assertEqual([1, 2, 3, 4, 5], page_list(page))

    def test_seven_pages(self):
        page = self.page(2, 7)
        self.assertEqual([1, 2, 3, 4, 5, 6, 7], page_list(page))

    def test_1_of_8_pages(self):
        page = self.page(1, 8)
        self.assertEqual([1, 2, 3, 4, 5, None, 8], page_list(page))

    def test_2_of_8_pages(self):
        page = self.page(2, 8)
        self.assertEqual([1, 2, 3, 4, 5, None, 8], page_list(page))

    def test_3_of_8_pages(self):
        page = self.page(3, 8)
        self.assertEqual([1, 2, 3, 4, 5, None, 8], page_list(page))

    def test_4_of_8_pages(self):
        page = self.page(4, 8)
        self.assertEqual([1, 2, 3, 4, 5, None, 8], page_list(page))

    def test_5_of_8_pages(self):
        page = self.page(5, 8)
        self.assertEqual([1, None, 4, 5, 6, 7, 8], page_list(page))

    def test_6_of_8_pages(self):
        page = self.page(6, 8)
        self.assertEqual([1, None, 4, 5, 6, 7, 8], page_list(page))

    def test_7_of_8_pages(self):
        page = self.page(7, 8)
        self.assertEqual([1, None, 4, 5, 6, 7, 8], page_list(page))

    def test_8_of_8_pages(self):
        page = self.page(8, 8)
        self.assertEqual([1, None, 4, 5, 6, 7, 8], page_list(page))

    def test_5_of_9_pages(self):
        page = self.page(5, 9)
        self.assertEqual([1, None, 4, 5, 6, None, 9], page_list(page))


class CurrentURLTestCase(TestCase):
    def mock_context(self, url):
        mock_request = mock.Mock(spec_set=['path', 'GET'])
        url_parts = urlparse(url)
        mock_request.path = url_parts.path
        mock_request.GET = OrderedDict(parse_qsl(url_parts.query))
        return {'request': mock_request}


class TestAddFilterToCurrentURL(CurrentURLTestCase):
    def test_empty(self):
        context = self.mock_context('/foo')
        out = add_filter_to_current_url(context, 'test', 1)
        self.assertEqual('/foo?test=1', out)

    def test_change(self):
        context = self.mock_context('/foo?test=1')
        out = add_filter_to_current_url(context, 'test', 2)
        self.assertEqual('/foo?test=2', out)

    def test_other(self):
        context = self.mock_context('/foo?bar=1')
        out = add_filter_to_current_url(context, 'test', 2)
        self.assertEqual('/foo?bar=1&test=2', out)


class TestDropFilterFromCurrentURL(CurrentURLTestCase):
    def test_empty(self):
        context = self.mock_context('/foo')
        out = drop_filter_from_current_url(context, 'test')
        self.assertEqual('/foo', out)

    def test_only(self):
        context = self.mock_context('/foo?test=1')
        out = drop_filter_from_current_url(context, 'test')
        self.assertEqual('/foo', out)

    def test_missing(self):
        context = self.mock_context('/foo?bar=1')
        out = drop_filter_from_current_url(context, 'test')
        self.assertEqual('/foo?bar=1', out)

    def test_with_others(self):
        context = self.mock_context('/foo?bar=1&test=2')
        out = drop_filter_from_current_url(context, 'test')
        self.assertEqual('/foo?bar=1', out)


class TestPaginationControl(CurrentURLTestCase):
    def test_one_page(self):
        page = self.page(1, 1)
        out = pagination_control(self.mock_context('/test'), page)
        self.assertEqual('', out)

    def test_first_page(self):
        page = self.page(1, 3)
        out = pagination_control(self.mock_context('/test'), page)
        expected_prev = (
            '<li class="disabled"><span aria-hidden="true">&laquo;</span>'
            '</li>')
        expected_next = (
            '<li><a href="/test?page=2" aria-label="Next">'
            '<span aria-hidden="true">&raquo;</span></a></li>')
        self.assertInHTML(expected_prev, out)
        self.assertInHTML(expected_next, out)

    def test_middle_page(self):
        page = self.page(2, 3)
        out = pagination_control(self.mock_context('/test'), page)
        expected_prev = (
            '<li><a href="/test" aria-label="Previous">'
            '<span aria-hidden="true">&laquo;</span></a></li>')
        expected_next = (
            '<li><a href="/test?page=3" aria-label="Next">'
            '<span aria-hidden="true">&raquo;</span></a></li>')
        self.assertInHTML(expected_prev, out)
        self.assertInHTML(expected_next, out)

    def test_last_page(self):
        page = self.page(3, 3)
        out = pagination_control(self.mock_context('/test'), page)
        expected_prev = (
            '<li><a href="/test?page=2" aria-label="Previous">'
            '<span aria-hidden="true">&laquo;</span></a></li>')
        expected_next = (
            '<li class="disabled"><span aria-hidden="true">&raquo;</span>'
            '</li>')
        self.assertInHTML(expected_prev, out)
        self.assertInHTML(expected_next, out)

    def test_deep_middle_page(self):
        page = self.page(5, 9)
        out = pagination_control(self.mock_context('/test'), page)
        expected_spacer = (
            '<li class="disabled"><span aria-hidden="true">&hellip;</span>'
            '</li>')
        self.assertInHTML(expected_spacer, out)


class TestCanReparseMDNImport(TestCase):

    def can_reparse(self, has_perm):
        """Call can_reparse_mdn_import with mocked data."""
        mock_user = mock.Mock(spec_set=['has_perm'])
        mock_user.has_perm.return_value = has_perm
        context = {}
        return can_reparse_mdn_import(context, mock_user)

    @override_settings(MDN_SHOW_REPARSE=True)
    def test_with_permission(self):
        self.assertTrue(self.can_reparse(True))

    @override_settings(MDN_SHOW_REPARSE=True)
    def test_without_permission(self):
        self.assertFalse(self.can_reparse(False))

    @override_settings(MDN_SHOW_REPARSE=False)
    def test_setting_off(self):
        self.assertFalse(self.can_reparse(True))
