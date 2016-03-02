# -*- coding: utf-8 -*-
"""Tests for v1 API viewsets."""
from __future__ import unicode_literals
from datetime import datetime
from json import dumps, loads
from pytz import UTC

import mock

from webplatformcompat.history import Changeset
from webplatformcompat.models import Browser, Feature, Version
from webplatformcompat.v2.viewsets import ViewFeaturesViewSet

from .base import APITestCase, NamespaceMixin
from ..test_viewsets import (
    TestCascadeDeleteGeneric, TestUserBaseViewset, TestViewFeatureBaseViewset)


class TestBrowserViewset(APITestCase):
    """Test common viewset functionality through the browsers viewset."""

    def test_get_browser_detail(self):
        browser = self.create(
            Browser,
            slug='firefox',
            name={'en': 'Firefox'},
            note={'en': 'Uses Gecko for its web browser engine'})
        url = self.full_api_reverse('browser-detail', pk=browser.pk)
        response = self.client.get(url)
        history_pk = browser.history.get().pk
        expected_content = {
            'links': {'self': url},
            'data': {
                'id': str(browser.pk),
                'type': 'browsers',
                'attributes': {
                    'slug': 'firefox',
                    'name': {'en': 'Firefox'},
                    'note': {'en': 'Uses Gecko for its web browser engine'},
                },
                'relationships': {
                    'versions': {
                        'data': [],
                        'links': {
                            'self': url + '/relationships/versions',
                            'related': url + '/versions',
                        },
                    },
                    'history_current': {
                        'data': {
                            'type': 'historical_browsers',
                            'id': str(history_pk),
                        },
                        'links': {
                            'self': url + '/relationships/history_current',
                            'related': url + '/history_current',
                        },
                    },
                    'history': {
                        'data': [
                            {'type': 'historical_browsers',
                             'id': str(history_pk)},
                        ],
                        'links': {
                            'self': url + '/relationships/history',
                            'related': url + '/history',
                        },
                    }
                },
            },
        }
        actual_content = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_content, actual_content)

    def test_get_browser_list(self):
        firefox = self.create(
            Browser,
            slug='firefox', name={'en': 'Firefox'},
            note={'en': 'Uses Gecko for its web browser engine'})
        chrome = self.create(Browser, slug='chrome', name={'en': 'Chrome'})
        url = self.full_api_reverse('browser-list')
        response = self.client.get(url)
        firefox_history_id = str(firefox.history.get().pk)
        chrome_history_id = str(chrome.history.get().pk)
        expected_content = {
            'data': [
                {
                    'links': {
                        'self': '%s/%s' % (url, firefox.pk),
                    },
                    'id': str(firefox.pk),
                    'type': 'browsers',
                    'attributes': {
                        'slug': 'firefox',
                        'name': {'en': 'Firefox'},
                        'note': {
                            'en': 'Uses Gecko for its web browser engine',
                        },
                    },
                    'relationships': {
                        'versions': {
                            'data': [],
                        },
                        'history_current': {
                            'data': {
                                'type': 'historical_browsers',
                                'id': firefox_history_id,
                            },
                        },
                        'history': {
                            'data': [
                                {'type': 'historical_browsers',
                                 'id': firefox_history_id},
                            ],
                        },
                    },
                }, {
                    'links': {
                        'self': '%s/%s' % (url, chrome.pk),
                    },
                    'id': '%s' % chrome.pk,
                    'type': 'browsers',
                    'attributes': {
                        'slug': 'chrome',
                        'name': {'en': 'Chrome'},
                        'note': None,
                    },
                    'relationships': {
                        'versions': {
                            'data': [],
                        },
                        'history_current': {
                            'data': {
                                'type': 'historical_browsers',
                                'id': chrome_history_id,
                            },
                        },
                        'history': {
                            'data': [
                                {'type': 'historical_browsers',
                                 'id': chrome_history_id},
                            ],
                        },
                    },
                },
            ],
            'links': {
                'self': url,
                'prev': None,
                'next': None,
            },
            'meta': {
                'count': 2,
            },
        }
        actual_content = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_content, actual_content)

    def test_get_browsable_api(self):
        browser = self.create(Browser)
        url = self.api_reverse('browser-list')
        response = self.client.get(url, HTTP_ACCEPT='text/html')
        history_pk = browser.history.get().pk
        expected_data = {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [{
                'id': browser.pk,
                'slug': '',
                'name': None,
                'note': None,
                'history': [history_pk],
                'history_current': history_pk,
                'versions': [],
            }]}
        self.assertDataEqual(response.data, expected_data)
        self.assertTrue(response['content-type'].startswith('text/html'))

    def test_get_related_versions_empty(self):
        browser = self.create(Browser)
        url = self.full_api_reverse('browser-versions', pk=browser.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {
                'self': url,
                'next': None,
                'prev': None,
            },
            'data': [],
            'meta': {'count': 0}
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_related_versions_populated(self):
        browser = self.create(Browser)
        version1 = self.create(Version, browser=browser, version='1.0')
        url = self.full_api_reverse('browser-versions', pk=browser.pk)
        response = self.client.get(url)
        vhistory = str(version1.history.all()[0].history_id)

        expected_content = {
            'links': {
                'self': url,
                'next': None,
                'prev': None,
            },
            'data': [
                {
                    'links': {
                        'self': self.full_api_reverse(
                            'version-detail', pk=version1.pk)
                    },
                    'id': str(version1.pk),
                    'type': 'versions',
                    'attributes': {
                        'version': '1.0',
                        'status': 'unknown',
                        'release_notes_uri': None,
                        'release_day': None,
                        'retirement_day': None,
                        'note': None,
                        'order': 0,
                    },
                    'relationships': {
                        'browser': {
                            'data': {
                                'type': 'browsers',
                                'id': str(browser.pk),
                            },
                        },
                        'supports': {
                            'data': [],
                        },
                        'history_current': {
                            'data': {
                                'type': 'historical_versions',
                                'id': vhistory,
                            },
                        },
                        'history': {
                            'data': [{
                                'type': 'historical_versions',
                                'id': vhistory,
                            }],
                        },
                    },
                },
            ],
            'meta': {'count': 1},
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_relationship_versions_empty(self):
        browser = self.create(Browser)
        url = self.full_api_reverse(
            'browser-relationships-versions', pk=browser.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'browser-versions', pk=browser.pk)
            },
            'data': [],
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_relationship_versions_populated(self):
        browser = self.create(Browser)
        version1 = self.create(Version, browser=browser, version='1.0')
        url = self.full_api_reverse(
            'browser-relationships-versions', pk=browser.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'browser-versions', pk=browser.pk)
            },
            'data': [
                {'type': 'versions', 'id': str(version1.pk)},
            ],
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_related_history_current(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'},
            _history_date=datetime(2015, 12, 23, 16, 40, 18, 648045, UTC))
        browser_url = self.full_api_reverse('browser-detail', pk=browser.pk)
        url = self.full_api_reverse('browser-history-current', pk=browser.pk)
        history = browser.history.all()[0]
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, url)
        expected_content = {
            'links': {
                'self': url
            },
            'data': {
                'id': str(history.history_id),
                'type': 'historical_browsers',
                'attributes': {
                    'event': 'created',
                    'date': self.dt_json(history.history_date),
                    'archive_data': {
                        'id': str(browser.id),
                        'type': 'browsers',
                        'attributes': {
                            'slug': 'browser',
                            'name': {'en': 'A Browser'},
                            'note': None,
                        },
                        'relationships': {
                            'history_current': {
                                'data': {
                                    'type': 'historical_browsers',
                                    'id': str(history.pk),
                                },
                            },
                            'versions': {'data': []}
                        },
                        'links': {'self': browser_url},
                    },
                },
                'relationships': {
                    'browser': {
                        'data': {'type': 'browsers', 'id': str(browser.pk)},
                        'links': {
                            'self': self.full_api_reverse(
                                'historicalbrowser-relationships-browser',
                                pk=history.pk),
                            'related': self.full_api_reverse(
                                'historicalbrowser-browser', pk=history.pk)
                        },
                    },
                    'changeset': {
                        'data': {
                            'type': 'changesets',
                            'id': str(history.history_changeset_id),
                        },
                        'links': {
                            'self': self.full_api_reverse(
                                'historicalbrowser-relationships-changeset',
                                pk=history.pk),
                            'related': self.full_api_reverse(
                                'historicalbrowser-changeset', pk=history.pk)
                        },
                    },
                }
            },
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_related_history(self):
        browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'})
        self.create(Browser, slug='other', name={'en': 'Other Browser'})
        url = self.api_reverse('browser-history', pk=browser.pk)
        history = browser.history.all()[0]
        response = self.client.get(url)
        self.assertEqual(200, response.status_code, url)
        response_data = loads(response.content.decode('utf8'))
        self.assertEqual(response_data['meta']['count'], 1)
        self.assertEqual(
            response_data['data'][0]['id'], str(history.history_id))

    def test_post_minimal(self):
        self.login_user()
        data = {'slug': 'firefox', 'name': '{"en": "Firefox"}'}
        response = self.client.post(self.api_reverse('browser-list'), data)
        self.assertEqual(201, response.status_code, response.data)
        browser = Browser.objects.get()
        history_pk = browser.history.get().pk
        expected_data = {
            'id': browser.pk,
            'slug': 'firefox',
            'name': {'en': 'Firefox'},
            'note': None,
            'history': [history_pk],
            'history_current': history_pk,
            'versions': [],
        }
        self.assertDataEqual(response.data, expected_data)

    @mock.patch('webplatformcompat.signals.update_cache_for_instance')
    def test_put_as_json_api(self, mock_update):
        """If content is application/vnd.api+json, put is partial."""
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        data = dumps({
            'data': {
                'id': str(browser.pk),
                'type': 'browsers',
                'attributes': {
                    'name': {
                        'en': 'New Name'
                    }
                }
            }
        })
        url = self.api_reverse('browser-detail', pk=browser.pk)
        mock_update.reset_mock()
        response = self.client.put(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)
        histories = browser.history.all()
        expected_data = {
            'id': browser.pk,
            'slug': 'browser',
            'name': {'en': 'New Name'},
            'note': None,
            'history': [h.pk for h in histories],
            'history_current': histories[0].pk,
            'versions': [],
        }
        self.assertDataEqual(response.data, expected_data)
        mock_update.assert_has_calls([
            mock.call('User', self.user.pk, mock.ANY),
            mock.call('Browser', browser.pk, mock.ANY),
        ])
        self.assertEqual(mock_update.call_count, 2)

    @mock.patch('webplatformcompat.signals.update_cache_for_instance')
    def test_put_in_changeset(self, mock_update):
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        changeset = Changeset.objects.create(user=self.user)
        data = dumps({
            'browsers': {
                'name': {
                    'en': 'New Name'
                }
            }
        })
        url = self.api_reverse('browser-detail', pk=browser.pk)
        url += '?use_changeset=%s' % changeset.pk
        mock_update.reset_mock()
        mock_update.side_effect = Exception('not called')
        response = self.client.put(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)

    def test_put_as_json(self):
        """If content is application/json, put is full put."""
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        data = {'name': '{"en": "New Name"}'}
        url = self.api_reverse('browser-detail', pk=browser.pk)
        response = self.client.put(url, data=data)
        self.assertEqual(200, response.status_code, response.data)
        histories = browser.history.all()
        expected_data = {
            'id': browser.pk,
            'slug': 'browser',
            'name': {'en': 'New Name'},
            'note': None,
            'history': [h.pk for h in histories],
            'history_current': histories[0].pk,
            'versions': [],
        }
        self.assertDataEqual(response.data, expected_data)

    @mock.patch('webplatformcompat.signals.update_cache_for_instance')
    def test_delete(self, mock_update):
        self.login_user(groups=['change-resource', 'delete-resource'])
        browser = self.create(Browser, slug='firesux', name={'en': 'Firesux'})
        url = self.api_reverse('browser-detail', pk=browser.pk)
        mock_update.reset_mock()
        response = self.client.delete(url)
        self.assertEqual(204, response.status_code, response.content)
        self.assertFalse(Browser.objects.filter(pk=browser.pk).exists())
        mock_update.assert_has_calls([
            mock.call('User', self.user.pk, mock.ANY),
            mock.call('Browser', browser.pk, mock.ANY),
        ])
        self.assertEqual(mock_update.call_count, 2)

    def test_delete_not_allowed(self):
        self.login_user()
        browser = self.create(
            Browser, slug='browser', name={'en': 'Old Name'})
        url = self.api_reverse('browser-detail', pk=browser.pk)
        response = self.client.delete(url)
        self.assertEqual(403, response.status_code)
        expected_data = {
            'detail': 'You do not have permission to perform this action.'
        }
        self.assertDataEqual(response.data, expected_data)

    @mock.patch('webplatformcompat.signals.update_cache_for_instance')
    def test_delete_in_changeset(self, mock_update):
        self.login_user(groups=['change-resource', 'delete-resource'])
        browser = self.create(
            Browser, slug='internet_exploder',
            name={'en': 'Internet Exploder'})
        url = self.api_reverse('browser-detail', pk=browser.pk)
        url += '?use_changeset=%d' % self.changeset.id
        mock_update.reset_mock()
        mock_update.side_effect = Exception('not called')
        response = self.client.delete(url)
        self.assertEqual(204, response.status_code, response.content)
        self.assertFalse(Browser.objects.filter(pk=browser.pk).exists())

    def test_options(self):
        self.login_user()
        browser = self.create(Browser)
        url = self.api_reverse('browser-detail', pk=browser.pk)
        response = self.client.options(url)
        self.assertEqual(200, response.status_code, response.content)
        expected_keys = {'actions', 'description', 'name', 'parses', 'renders'}
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_query_reserved_namespace_is_error(self):
        """Test that an unknown, lowercase query parameter is an error."""
        url = self.api_reverse('browser-list')
        response = self.client.get(url, {'foo': 'bar'})
        self.assertEqual(400, response.status_code, response.content)
        expected = {
            'errors': [{
                'status': '400',
                'detail': 'Query parameter "foo" is invalid.',
                'source': {'parameter': 'foo'}
            }]
        }
        self.assertEqual(expected, loads(response.content.decode('utf8')))

    def test_unreserved_query_is_ignored(self):
        """Test that unknown but unreserved query strings are ignored."""
        url = self.api_reverse('browser-list')
        params = {
            'camelCase': 'ignored',
            'hyphen-split': 'ignored',
            'low_line': 'ignored',
        }
        response = self.client.get(url, params)
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(0, response.data['count'])

    def test_page_params_is_ok(self):
        """
        Test that pagination params are OK.

        bug 1243128 will change these to page[number] and page[size].
        """
        for number in range(5):
            self.create(Browser, slug='slug%d' % number)
        url = self.api_reverse('browser-list')
        pagination = {'page': 2, 'page_size': 2}
        response = self.client.get(url, pagination)
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(5, response.data['count'])

    def assert_param_not_implemented(self, key, value):
        """Assert that a valid but optional parameter is not implemented."""
        url = self.api_reverse('browser-list')
        response = self.client.get(url, {key: value})
        self.assertEqual(400, response.status_code, response.content)
        expected = {
            'errors': [{
                'status': '400',
                'detail': 'Query parameter "%s" is not implemented.' % key,
                'source': {'parameter': key}
            }]
        }
        self.assertEqual(expected, loads(response.content.decode('utf8')))

    def test_param_include_not_implemented(self):
        """
        Confirm parameter include is unimplemented.

        TODO: bug 1243190, use param 'include' for included resources.
        """
        self.assert_param_not_implemented('include', 'versions')

    def test_param_fields_unimplemented(self):
        """
        Confirm JSON API v1.0 parameter 'fields' is unimplemented.

        TODO: bug 1252973, use param 'fields' for sparse fieldsets.
        """
        self.assert_param_not_implemented('fields', 'name')
        self.assert_param_not_implemented('fields[browsers]', 'slug,name')

    def test_param_sort_unimplemented(self):
        """
        Confirm JSON API v1.0 parameter 'sort' is unimplemented.

        TODO: bug 1252973, use param 'fields' for sparse fieldsets.
        """
        self.assert_param_not_implemented('sort', 'name')


class TestFeatureViewSet(APITestCase):
    """Test FeatureViewSet."""

    def test_filter_by_slug(self):
        parent = self.create(Feature, slug='parent', name={'en': 'Parent'})
        feature = self.create(
            Feature, slug='feature', parent=parent, name={'en': 'A Feature'})
        self.create(Feature, slug='other', name={'en': 'Other'})
        response = self.client.get(
            self.api_reverse('feature-list'), {'filter[slug]': 'feature'})
        self.assertEqual(200, response.status_code, response.data)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(feature.id, response.data['results'][0]['id'])

    def test_filter_by_parent(self):
        parent = self.create(Feature, slug='parent', name={'en': 'Parent'})
        feature = self.create(
            Feature, slug='feature', parent=parent, name={'en': 'A Feature'})
        self.create(Feature, slug='other', name={'en': 'Other'})
        response = self.client.get(
            self.api_reverse('feature-list'),
            {'filter[parent]': str(parent.id)})
        self.assertEqual(200, response.status_code, response.data)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(feature.id, response.data['results'][0]['id'])

    def test_filter_by_no_parent(self):
        parent = self.create(Feature, slug='parent', name={'en': 'Parent'})
        self.create(
            Feature, slug='feature', parent=parent, name={'en': 'The Feature'})
        other = self.create(Feature, slug='other', name={'en': 'Other'})
        response = self.client.get(
            self.api_reverse('feature-list'), {'filter[parent]': ''})
        self.assertEqual(200, response.status_code, response.data)
        self.assertEqual(2, response.data['count'])
        self.assertEqual(parent.id, response.data['results'][0]['id'])
        self.assertEqual(other.id, response.data['results'][1]['id'])

    def test_filter_by_unknown_param(self):
        """Test that filtering by an unknown parameter is an error."""
        response = self.client.get(
            self.api_reverse('feature-list'), {'filter[unknown]': 'value'})
        self.assertEqual(400, response.status_code, response.data)
        expected_content = {
            'errors': [{
                'detail': 'Unknown filter "unknown" requested.',
                'status': '400'
            }]
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_related_parent_null(self):
        feature = self.create(Feature)
        url = self.full_api_reverse('feature-parent', pk=feature.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {'self': url},
            'data': None,
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_related_parent_set(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        url = self.full_api_reverse('feature-parent', pk=feature.pk)
        response = self.client.get(url)
        phistory = str(parent.history.all()[0].history_id)

        expected_content = {
            'links': {
                'self': url
            },
            'data': {
                'id': str(parent.pk),
                'type': 'features',
                'attributes': {
                    'slug': 'parent',
                    'name': None,
                    'experimental': False,
                    'mdn_uri': None,
                    'obsolete': False,
                    'stable': True,
                    'standardized': True,
                },
                'relationships': {
                    'children': {
                        'data': [{
                            'type': 'features',
                            'id': str(feature.pk),
                        }],
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-children',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-children', pk=parent.pk),
                        },
                    },
                    'parent': {
                        'data': None,
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-parent',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-parent', pk=parent.pk),
                        },
                    },
                    'supports': {
                        'data': [],
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-supports',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-supports', pk=parent.pk),
                        },
                    },
                    'references': {
                        'data': [],
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-references',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-references', pk=parent.pk),
                        },
                    },
                    'history_current': {
                        'data': {
                            'type': 'historical_features',
                            'id': phistory,
                        },
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-history-current',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-history-current', pk=parent.pk),
                        },
                    },
                    'history': {
                        'data': [{
                            'type': 'historical_features',
                            'id': phistory,
                        }],
                        'links': {
                            'self': self.full_api_reverse(
                                'feature-relationships-history',
                                pk=parent.pk),
                            'related': self.full_api_reverse(
                                'feature-history', pk=parent.pk),
                        },
                    },
                },
            },
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_relationship_parent_null(self):
        feature = self.create(Feature)
        url = self.full_api_reverse(
            'feature-relationships-parent', pk=feature.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'feature-parent', pk=feature.pk)
            },
            'data': None,
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_get_relationship_parent_set(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        url = self.full_api_reverse(
            'feature-relationships-parent', pk=feature.pk)
        response = self.client.get(url)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'feature-parent', pk=feature.pk)
            },
            'data': {
                'type': 'features', 'id': str(parent.pk),
            },
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_set_parent_to_null(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        url = self.full_api_reverse('feature-detail', pk=feature.pk)
        data = dumps({
            'data': {
                'id': str(feature.pk),
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': None
                    }
                }
            }
        })
        response = self.client.patch(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.content)
        actual_data = loads(response.content.decode('utf-8'))
        self.assertIsNone(
            actual_data['data']['relationships']['parent']['data'])

    def test_set_relationship_parent_to_null(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature', parent=parent)
        url = self.full_api_reverse(
            'feature-relationships-parent', pk=feature.pk)
        data = dumps({'data': None})
        response = self.client.patch(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.content)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'feature-parent', pk=feature.pk)
            },
            'data': None,
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_set_relationship_parent(self):
        parent = self.create(Feature, slug='parent')
        feature = self.create(Feature, slug='feature')
        url = self.full_api_reverse(
            'feature-relationships-parent', pk=feature.pk)
        data = dumps({
            'data': {
                'type': 'features', 'id': str(parent.pk),
            }
        })
        response = self.client.patch(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.content)
        expected_content = {
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'feature-parent', pk=feature.pk)
            },
            'data': {
                'type': 'features', 'id': str(parent.pk),
            },
        }
        actual_content = response.content.decode('utf-8')
        self.assertJSONEqual(actual_content, expected_content)

    def test_set_children(self):
        feature = self.create(Feature, slug='feature')
        child1 = self.create(Feature, slug='child1', parent=feature)
        child2 = self.create(Feature, slug='child2', parent=feature)
        url = self.full_api_reverse('feature-detail', pk=feature.pk)
        new_children = [
            {'type': 'features', 'id': str(child2.pk)},
            {'type': 'features', 'id': str(child1.pk)},
        ]
        data = dumps({
            'data': {
                'id': str(feature.pk),
                'type': 'features',
                'relationships': {
                    'children': {
                        'data': new_children,
                    }
                }
            }
        })
        response = self.client.patch(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.content)
        actual_data = loads(response.content.decode('utf-8'))
        self.assertEqual(
            actual_data['data']['relationships']['children']['data'],
            new_children)

    def test_set_relationship_children(self):
        feature = self.create(Feature, slug='feature')
        child1 = self.create(Feature, slug='child1', parent=feature)
        child2 = self.create(Feature, slug='child2', parent=feature)
        url = self.full_api_reverse(
            'feature-relationships-children', pk=feature.pk)
        new_children = [
            {'type': 'features', 'id': str(child2.pk)},
            {'type': 'features', 'id': str(child1.pk)},
        ]
        data = dumps({'data': new_children})
        response = self.client.patch(
            url, data=data, content_type='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.content)
        expected = {
            'data': new_children,
            'links': {
                'self': url,
                'related': self.full_api_reverse(
                    'feature-children', pk=feature.pk)
            }
        }
        self.assertJSONEqual(response.content.decode('utf8'), expected)


class TestHistoricaBrowserViewset(APITestCase):
    """Test common historical viewset functionality through browsers."""

    def setUp(self):
        self.browser = self.create(
            Browser, slug='browser', name={'en': 'A Browser'},
            _history_date=datetime(2014, 8, 25, 20, 50, 38, 868903, UTC))
        self.history = self.browser.history.all()[0]

    def test_get_historical_browser_detail(self):
        url = self.full_api_reverse(
            'historicalbrowser-detail', pk=self.history.pk)
        response = self.client.get(url, HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)

        expected_json = {
            'links': {'self': url},
            'data': {
                'id': str(self.history.pk),
                'type': 'historical_browsers',
                'attributes': {
                    'date': self.dt_json(self.browser._history_date),
                    'event': 'created',
                    'archive_data': {
                        'id': str(self.browser.pk),
                        'type': 'browsers',
                        'attributes': {
                            'slug': 'browser',
                            'name': {'en': 'A Browser'},
                            'note': None,
                        },
                        'relationships': {
                            'history_current': {
                                'data': {
                                    'type': 'historical_browsers',
                                    'id': str(self.history.pk),
                                },
                            },
                            'versions': {'data': []},
                        },
                        'links': {
                            'self': self.full_api_reverse(
                                'browser-detail', pk=self.browser.pk)
                        }
                    },
                },
                'relationships': {
                    'browser': {
                        'data': {
                            'type': 'browsers', 'id': str(self.browser.pk)},
                        'links': {
                            'self': url + '/relationships/browser',
                            'related': url + '/browser',
                        },
                    },
                    'changeset': {
                        'data': {
                            'type': 'changesets',
                            'id': str(self.history.history_changeset_id),
                        },
                        'links': {
                            'self': url + '/relationships/changeset',
                            'related': url + '/changeset',
                        },
                    },
                },
            },
        }
        actual_json = loads(response.content.decode('utf-8'))
        self.assertDataEqual(expected_json, actual_json)

    def test_related_browser(self):
        url = self.full_api_reverse(
            'historicalbrowser-browser', pk=self.history.pk)
        response = self.client.get(url, HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)

    def test_relationships_browser(self):
        url = self.full_api_reverse(
            'historicalbrowser-relationships-browser', pk=self.history.pk)
        response = self.client.get(url, HTTP_ACCEPT='application/vnd.api+json')
        self.assertEqual(200, response.status_code, response.data)


class TestCascadeDelete(NamespaceMixin, TestCascadeDeleteGeneric):
    """Test cascading deletes."""


class TestUserViewset(NamespaceMixin, TestUserBaseViewset):
    """Test users/me UserViewSet."""


class TestViewFeatureViewset(NamespaceMixin, TestViewFeatureBaseViewset):
    """Test helper functions on ViewFeaturesViewSet."""

    def setUp(self):
        super(TestViewFeatureViewset, self).setUp()
        self.view = ViewFeaturesViewSet()
