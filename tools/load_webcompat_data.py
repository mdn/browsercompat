#!/usr/bin/env python

from __future__ import print_function

from collections import OrderedDict
import getpass
import json
import logging
import os.path
import re
import sys
import urllib

import requests


logger = logging.getLogger('populate_data')
COMPAT_DATA_FILENAME = "data-human.json"
COMPAT_DATA_URL = (
    "https://raw.githubusercontent.com/webplatform/compatibility-data"
    "/master/data-human.json")


def get_session(base_url, user, password):
    '''Create an authenticated connection to the API'''
    session = requests.Session()
    next_path = '/api/browsers'
    params = {'next': next_path}
    response = session.get(base_url + '/api-auth/login/', params=params)
    try:
        csrf = response.cookies['csrftoken']
    except KeyError:
        raise Exception("No CSRF in response", response)
    data = {
        'username': user,
        'password': password,
        'csrfmiddlewaretoken': csrf,
        'next': next_path
    }
    response = session.post(
        base_url + '/api-auth/login/', params=params, data=data)
    if response.url == base_url + next_path:
        logger.info("Logged into " + base_url)
        session.base_url = base_url
        return session
    else:
        raise Exception('Problem logging in.', response)


def verify_empty_api(session):
    '''Verify that no data is loaded into this API'''
    response = session.get(
        session.base_url + '/api/browsers',
        headers={'content-type': 'application/vnd.api+json'})
    expected = {'browsers': []}
    actual = response.json()
    if response.json() != expected:
        raise Exception('API already has browser data', actual)


def get_compat_data(filename, url):
    if not os.path.exists(filename):
        logger.info("Downloading " + filename)
        urllib.urlretrieve(url, filename)
    else:
        logger.info("Using existing " + filename)

    with open(filename, 'r') as f:
        compat_data = json.load(f)
    return compat_data


def load_compat_data(session, compat_data):
    '''Load a dictionary of compatiblity data into the API'''
    verify_empty_api(session)
    parsed_data = parse_compat_data(compat_data)
    return upload_compat_data(session, parsed_data)


def parse_compat_data(compat_data):
    parsed_data = {
        'browsers': OrderedDict(),
        'browser_versions': OrderedDict(),
    }

    for key, value in compat_data['data'].items():
        parse_compat_data_item(key, value, parsed_data)

    return parsed_data

version_re = re.compile("^[.\d]+$")


def slugify(word):
    return word.lower().replace(' ', '-')


def parse_compat_data_item(key, item, parsed_data):
    known_browsers = [
        "Chrome",
        "Firefox",
        "Internet Explorer",
        "Opera",
        "Safari",
        "Android",
        "Chrome for Android",
        "Chrome Mobile",
        "Firefox Mobile",
        "IE Mobile",
        "Opera Mobile",
        "Safari Mobile",
        "BlackBerry",
        "Firefox OS",
        "Opera Mini",
    ]
    browser_conversions = {
        "IE Phone": "IE Mobile",
        "Chrome for Andriod": "Chrome for Android",
        "Android Browser": "Android",
        "Chrome**": "Chrome",
        "Opera*": "Opera",
        "BlackBerry Browser": "BlackBerry",
        "Internet Explorer*": "Internet Explorer",
        "IE": "Internet Explorer",
        "Firefox mobile": "Firefox Mobile",
        "Windows Phone": "IE Mobile",
        "iOS Safari": "Safari Mobile",
    }
    version_ignore = [
        'notes',
    ]
    version_conversions = {
        "?": ""
    }
    known_versions = [
        "",
    ]

    if "breadcrumb" in item:
        assert "contents" in item
        assert "jsonselect" in item
        for env, rows in item['contents'].items():
            assert env in ('desktop', 'mobile')
            for feature, columns in rows.items():
                for raw_browser, versions in columns.items():
                    browser = browser_conversions.get(raw_browser, raw_browser)
                    assert browser in known_browsers, raw_browser
                    browser_slug = slugify(browser)
                    if browser_slug not in parsed_data['browsers']:
                        parsed_data['browsers'][browser_slug] = {
                            'slug': browser_slug,
                            'name': browser,
                        }
                    for raw_version in versions:
                        if raw_version in version_ignore:
                            continue
                        version = version_conversions.get(
                            raw_version, raw_version)
                        if version not in known_versions:
                            assert version_re.match(version), raw_version
                        v_ident = (browser_slug, version)
                        if v_ident not in parsed_data['browser_versions']:
                            parsed_data['browser_versions'][v_ident] = {
                                'version': version,
                                'status': 'unknown',
                            }

    else:
        for subkey, subitem in item.items():
            parse_compat_data_item(subkey, subitem, parsed_data)


def upload_compat_data(session, parsed_data):
    browser_ids = {}
    logger.info("Importing browsers...")
    for slug, browser in parsed_data['browsers'].items():
        data = {
            "slug": slug,
            "name": {'en': browser['name']}
        }
        browser_json = json.dumps({"browsers": data})
        response = session.post(
            session.base_url + '/api/browsers', data=browser_json,
            headers={
                'content-type': 'application/vnd.api+json',
                'X-CSRFToken': session.cookies['csrftoken']})
        assert response.status_code == 201, response.content
        browser_ids[slug] = response.json()['browsers']['id']
        if len(browser_ids) % 100 == 0:
            logger.info("Imported %d browsers..." % len(browser_ids))

    bv_ids = {}
    logger.info("Importing browser-versions...")
    for ident, bv in parsed_data['browser_versions'].items():
        browser_slug, version = ident
        data = {
            "version": version,
            "status": bv.get('status', 0),
            "links": {
                "browser": browser_ids[browser_slug]
            }
        }
        bv_json = json.dumps({"browser versions": data})
        response = session.post(
            session.base_url + '/api/browser-versions', data=bv_json,
            headers={
                'content-type': 'application/vnd.api+json',
                'X-CSRFToken': session.cookies['csrftoken']})
        assert response.status_code == 201
        bv_ids[ident] = response.json()['browser versions']['id']
        if len(bv_ids) % 100 == 0:
            logger.info("Imported %d browser-versions..." % len(bv_ids))

    return (
        ('browsers', len(browser_ids)),
        ('browser_versions', len(bv_ids)),
    )


if __name__ == '__main__':
    import argparse
    description = 'Initialize with compatibility data from webcompat project.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-a', '--api',
        help='Base URL of the API (default: http://localhost:8000)',
        default="http://localhost:8000")
    parser.add_argument(
        '-u', '--user',
        help='Username on API (default: prompt for username)')
    parser.add_argument(
        '-v', '--verbosity', action="count", default=0)
    args = parser.parse_args()

    # Setup logging
    verbosity = args.verbosity
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logger_name = 'populate_data'
    fmat = '%(levelname)s - %(message)s'
    if verbosity <= 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity == 2:
        level = logging.DEBUG
    else:
        level = logging.DEBUG
        logger_name = ''
        fmat = '%(name)s - %(levelname)s - %(message)s'
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
    user = args.user or raw_input("API username: ")
    password = getpass.getpass("API password: ")
    session = get_session(api, user, password)
    compat_data = get_compat_data(COMPAT_DATA_FILENAME, COMPAT_DATA_URL)
    counts = load_compat_data(session, compat_data)

    logger.info("Upload complete. Counts:")
    for name, count in counts:
        logger.info("  %s: %d" % (name, count))
