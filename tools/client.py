#!/usr/bin/env python
"""Client for accessing the API

This is a baby step toward a generally useful client.  As it matures, it may
grow features and get moved to its own repo.
"""

from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
from time import time
import logging

import requests

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Errors returned from API"""
    pass


class Client(object):
    """Client for talking to the web-platform-compat API."""

    def __init__(self, base_url):
        self.base_url = base_url
        self._session = None
        self.csrftoken = None
        self.changeset = None

    @property
    def session(self):
        """Return the session, creating if needed"""
        if not self._session:
            self._session = requests.Session()
        return self._session

    def request(
            self, method, resource_type, resource_id=None, params=None,
            data=None):
        """Request data from the API"""
        start = time()

        url = self.base_url + '/api/v1/' + resource_type
        if resource_id:
            url += '/' + resource_id

        # Setup parameters
        params = params or {}
        headers = {'content-type': 'application/vnd.api+json'}
        modify_methods = ('PUT', 'DELETE', 'PATCH')
        create_methods = ('POST',)
        change_methods = modify_methods + create_methods
        if method in change_methods and self.csrftoken:
            headers['X-CSRFToken'] = self.csrftoken
        if method in change_methods and self.changeset:
            params['changeset'] = self.changeset
        if method in create_methods:
            expected_statuses = [201]
        else:
            expected_statuses = [200]
        if data:
            data_json = dumps(data)
        else:
            data_json = None

        # Make the request
        rfunc = getattr(self.session, method.lower())
        response = rfunc(url, params=params, data=data_json, headers=headers)
        if response.status_code not in expected_statuses:
            raise APIException(
                'Unexpected response', response.status_code,
                response.content)

        end = time()
        logger.debug('%s %s completed in %0.1fs', method, url, end - start)
        return response.json()

    def login(self, user, password, next_path='/api/v1/browsers'):
        """Log into the API."""
        # Get login page
        params = {'next': next_path}
        url = self.base_url + '/api-auth/login/'
        response = self.session.get(url, params=params)
        csrf = response.cookies['csrftoken']

        # Post user credentials
        data = {
            'username': user,
            'password': password,
            'csrfmiddlewaretoken': csrf,
            'next': next_path
        }

        response = self.session.post(
            self.base_url + '/api-auth/login/', params=params, data=data)
        if response.url == self.base_url + next_path:
            logger.info("Logged into " + self.base_url)
            self.csrftoken = self.session.cookies['csrftoken']
        else:
            raise Exception('Problem logging in.', response)

    def open_changeset(self):
        """Open a changeset for multiple items"""
        assert not self.changeset, 'A changeset is already open!'
        response = self.create('changesets', {})
        self.changeset = response['id']

    def close_changeset(self):
        """Close a changeset for multiple items"""
        assert self.changeset, 'There is no open changeset!'
        data = {'changesets': {'closed': True}}
        self.request('PUT', 'changesets', self.changeset, data=data)
        self.changeset = None

    def count(self, resource_type):
        """Return the current count for a resource type"""
        response = self.request('GET', resource_type)
        return response['meta']['pagination'][resource_type]['count']

    def create(self, resource_type, resource):
        """Create a resource in the API

        Keyword arguments:
        resource_type -- resource name, such as 'browsers'
        resource -- data as a Python dict, such as: {'slug': 'foo'}

        The return is a Python dict, such as: {'id': 1, 'slug': 'foo'}
        On failure, an APIException is raised.
        """
        data = {resource_type: resource}
        response = self.request('POST', resource_type, data=data)
        return response[resource_type]


if __name__ == "__main__":
    from math import log10, trunc
    import argparse
    import sys

    description = 'Demo client with resource count'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-a', '--api',
        help='Base URL of the API (default: http://localhost:8000)',
        default="http://localhost:8000")
    parser.add_argument(
        '-v', '--verbose', action="store_true",
        help='Print extra debug information')
    parser.add_argument(
        '-q', '--quiet', action="store_true",
        help='Only print warnings')
    parser.add_argument(
        '--all-data', action="store_true",
        help='Import all the data, rather than a subset')
    args = parser.parse_args()

    # Setup logging
    verbose = args.verbose
    quiet = args.quiet
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logger_name = __name__
    fmat = '%(levelname)s - %(message)s'
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
        logger_name = ''
        fmat = '%(name)s - %(levelname)s - %(message)s'
    else:
        level = logging.INFO
    formatter = logging.Formatter(fmat)
    console.setLevel(level)
    console.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(console)

    # Parse arguments
    api = args.api
    if api.endswith('/'):
        api = api[:-1]
    logger.info("Counting resources on %s" % api)

    # Get counts
    client = Client(api)
    resources = [
        'browsers', 'versions', 'features', 'supports', 'specifications',
        'maturities', 'sections', 'users']
    count = {}
    for r in resources:
        count[r] = client.count(r)

    max_resource_len = max([len(r) for r in resources])
    max_count = max(count.values())
    if max_count:
        max_count_len = trunc(log10(max(count.values()))) + 1
    else:
        max_count_len = 1
    for r in resources:
        print('{0:>{1}}: {2!s:>{3}}'.format(
            r, max_resource_len, count[r], max_count_len))
