#!/usr/bin/env python

from __future__ import print_function

import getpass
import json
import logging
import os.path
import re
import string
import sys
import urllib

import requests

try:
    input = raw_input  # Get the Py2 raw_input
except NameError:
    pass  # We're in Py3


logger = logging.getLogger('populate_data')
COMPAT_DATA_FILENAME = "data-human.json"
COMPAT_DATA_URL = (
    "https://raw.githubusercontent.com/webplatform/compatibility-data"
    "/master/data-human.json")
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
    "Opera Mini",
    "Opera Mobile",
    "Safari Mobile",
    "BlackBerry",
    "Firefox OS",
]
version_re = re.compile("^[.\d]+$")


def get_session(base_url, user, password):
    '''Create an authenticated connection to the API'''
    session = requests.Session()
    next_path = '/api/v1/browsers'
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
        session.base_url + '/api/v1/browsers',
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
        'browsers': dict(),
        'features': dict(),
        'feature_slugs': set(),
        'versions': dict(),
    }

    for key, value in compat_data['data'].items():
        parse_compat_data_item(key, value, parsed_data)

    return parsed_data


def slugify(word, attempt=0):
    raw = word.lower().encode('utf-8')
    out = []
    acceptable = string.ascii_lowercase + string.digits + '_-'
    for c in raw:
        if c in acceptable:
            out += str(c)
        else:
            out += '_'
    slugged = ''.join(out)
    while '__' in slugged:
        slugged = slugged.replace('__', '_')
    if attempt:
        suffix = str(attempt)
    else:
        suffix = ""
    return slugged[slice(50-len(suffix))] + suffix


def unique_slugify(word, existing):
    slug = slugify(word)
    attempt = 0
    while slug in existing:
        attempt += 1
        slug = slugify(word, attempt)
    existing.add(slug)
    return slug


def parse_compat_data_item(key, item, parsed_data):
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

    if "breadcrumb" in item:
        assert "contents" in item
        assert "jsonselect" in item
        assert "links" in item

        # Feature heirarchy
        url = item['links'][0]["url"]
        assert url.startswith('https://developer.mozilla.org/en-US/docs/')
        mdn_path = url.split('mozilla.org/', 1)[1]
        mdn_subpath = url.split('en-US/docs/', 1)[1]
        path_bits = mdn_subpath.split('/')
        feature_id = ()
        for bit in path_bits:
            last_feature_id = feature_id
            feature_id += (bit,)
            if feature_id not in parsed_data['features']:
                parsed_data['features'][feature_id] = {
                    'slug': unique_slugify(
                        '-'.join(feature_id), parsed_data['feature_slugs']),
                    'mdn_path': '/en-US/docs/' + '/'.join(path_bits),
                    'name': {'en': bit},
                    'parent_id': last_feature_id,
                }
        parent_feature_id = feature_id

        for env, rows in item['contents'].items():
            assert env in ('desktop', 'mobile')
            for feature, columns in rows.items():
                # Add feature
                feature_id = parent_feature_id + (feature,)
                if feature_id not in parsed_data['features']:
                    parsed_data['features'][feature_id] = {
                        'slug': unique_slugify(
                            '-'.join(feature_id),
                            parsed_data['feature_slugs']),
                        'mdn_path': mdn_path,
                        'name': {'en': feature},
                        'parent_id': parent_feature_id,
                    }

                # Add browser
                for raw_browser, versions in columns.items():
                    browser = browser_conversions.get(raw_browser, raw_browser)
                    assert browser in known_browsers, raw_browser
                    browser_id = known_browsers.index(browser)
                    if browser_id not in parsed_data['browsers']:
                        parsed_data['browsers'][browser_id] = {
                            'slug': slugify(browser),
                            'name': browser,
                        }

                    # Add version
                    for raw_version in versions:
                        if raw_version in version_ignore:
                            continue
                        version, version_id = convert_version(
                            browser_id, raw_version)
                        if version_id not in parsed_data['versions']:
                            parsed_data['versions'][version_id] = {
                                'version': version,
                            }

    else:
        for subkey, subitem in item.items():
            parse_compat_data_item(subkey, subitem, parsed_data)


def convert_version(browser_id, raw_version):
    version = "" if raw_version == "?" else raw_version
    if raw_version == '?':
        version = ""
    else:
        version = raw_version
    if version == "":
        version_id = (browser_id,)
    else:
        assert version_re.match(version), raw_version
        bits = tuple(int(x) for x in version.split('.'))
        if len(bits) == 1:
            # Prefer 12.0 format to 12 format
            version += '.0'
            bits += (0,)
        version_id = (browser_id,) + bits
    return version, version_id


def upload_compat_data(session, parsed_data):
    browser_api_ids = {}
    logger.info("Importing browsers...")
    for browser_id in sorted(parsed_data['browsers'].keys()):
        browser = parsed_data['browsers'][browser_id]
        data = {
            "slug": browser['slug'],
            "name": {'en': browser['name']}
        }
        browser_json = json.dumps({"browsers": data})
        response = session.post(
            session.base_url + '/api/v1/browsers', data=browser_json,
            headers={
                'content-type': 'application/vnd.api+json',
                'X-CSRFToken': session.cookies['csrftoken']})
        assert response.status_code == 201, response.content
        browser_api_ids[browser_id] = response.json()['browsers']['id']
        if len(browser_api_ids) % 100 == 0:
            logger.info("Imported %d browsers..." % len(browser_api_ids))

    version_api_ids = {}
    logger.info("Importing versions...")
    for version_id in sorted(parsed_data['versions'].keys()):
        version = parsed_data['versions'][version_id]
        browser_id = version_id[0]
        data = {
            "version": version['version'],
            "status": version.get('status', 'unknown'),
            "links": {
                "browser": browser_api_ids[browser_id]
            }
        }
        version_json = json.dumps({"versions": data})
        response = session.post(
            session.base_url + '/api/v1/versions', data=version_json,
            headers={
                'content-type': 'application/vnd.api+json',
                'X-CSRFToken': session.cookies['csrftoken']})
        assert response.status_code == 201, response.content
        version_api_ids[version_id] = response.json()['versions']['id']
        if len(version_api_ids) % 100 == 0:
            logger.info("Imported %d versions..." % len(version_api_ids))

    feature_api_ids = {(): None}
    logger.info("Importing features...")
    for feature_id in sorted(parsed_data['features'].keys()):
        feature = parsed_data['features'][feature_id]
        data = {
            "slug": feature["slug"],
            "mdn_path": feature["mdn_path"],
            "name": feature["name"],
            "links": {
                "parent": feature_api_ids[feature["parent_id"]]
            }
        }
        feature_json = json.dumps({"features": data})
        response = session.post(
            session.base_url + '/api/v1/features', data=feature_json,
            headers={
                'content-type': 'application/vnd.api+json',
                'X-CSRFToken': session.cookies['csrftoken']})
        assert response.status_code == 201, response.content
        feature_api_ids[feature_id] = response.json()['features']['id']
        if len(feature_api_ids) % 100 == 0:
            logger.info("Imported %d features..." % len(feature_api_ids))

    return (
        ('browsers', len(browser_api_ids)),
        ('versions', len(version_api_ids)),
        ('features', len(feature_api_ids)),
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
        '-v', '--verbose', action="store_true",
        help='Print extra debug information')
    parser.add_argument(
        '-q', '--quiet', action="store_true",
        help='Only print warnings')
    args = parser.parse_args()

    # Setup logging
    verbose = args.verbose
    quiet = args.quiet
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logger_name = 'populate_data'
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
    logger.info("Loading data into %s" % api)
    user = args.user or input("API username: ")
    password = getpass.getpass("API password: ")
    session = get_session(api, user, password)
    compat_data = get_compat_data(COMPAT_DATA_FILENAME, COMPAT_DATA_URL)
    counts = load_compat_data(session, compat_data)

    logger.info("Upload complete. Counts:")
    for name, count in counts:
        logger.info("  %s: %d" % (name, count))
