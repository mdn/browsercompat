#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `web-platform-compat.viewsets.UserViewSet` class."""
from __future__ import unicode_literals
from datetime import datetime
from json import loads
from pytz import UTC

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .base import APITestCase


class TestUserViewset(APITestCase):
    """Test users viewset"""

    def test_get_minimal(self):
        date_joined = datetime(2014, 9, 4, 17, 10, 21, 827311, UTC)
        user = User.objects.create(username='user', date_joined=date_joined)
        url = self.reverse('user-detail', pk=user.pk)
        response = self.client.get(url, HTTP_ACCEPT="application/vnd.api+json")
        expected_data = {
            'id': user.pk,
            'username': 'user',
            'created': self.dt_repr(date_joined),
            'agreement': 0,
            'permissions': ['change-resource'],
            'changesets': [],
        }
        self.assertDataEqual(response.data, expected_data)
        expected_content = {
            "users": {
                "id": str(user.pk),
                "username": 'user',
                "created": self.dt_json(date_joined),
                "agreement": 0,
                "permissions": ['change-resource'],
                "links": {"changesets": []},
            },
            "links": {
                "users.changesets": {
                    "href": (
                        "http://testserver/api/v1/changesets/"
                        "{users.changesets}"),
                    "type": "changesets"
                }
            }
        }
        actual_content = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_content, actual_content)

    def test_filter_by_username(self):
        date_joined = datetime(2014, 9, 4, 17, 10, 21, 827311, UTC)
        user = User.objects.create(username='user', date_joined=date_joined)
        User.objects.create(username='other')

        response = self.client.get(reverse('user-list'), {'username': 'user'})
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': user.pk,
                'username': 'user',
                "created": self.dt_repr(date_joined),
                'agreement': 0,
                'permissions': ['change-resource'],
                'changesets': [],
            }]}
        self.assertDataEqual(response.data, expected_data)
