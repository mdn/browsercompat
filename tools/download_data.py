#!/usr/bin/env python

from __future__ import print_function

import codecs
import json
import logging
import os.path
import sys

from client import Client

logger = logging.getLogger('tools.download_data')

resources = [
    'browsers',
    'versions',
    'features',
    'supports',
    'specifications',
    'maturities',
    'sections',
]


def download_data(client, base_dir=''):
    """Download data from the API"""
    counts = {}
    for resource in resources:
        # Get data from API
        data = client.get_resource_collection(resource)
        logger.info("Downloaded %d %s.", len(data[resource]), resource)
        counts[resource] = len(data[resource])

        # Remove history relations
        for item in data[resource]:
            del item['links']['history']
            del item['links']['history_current']
        if 'links' in data:
            del data['links']['%s.history' % resource]
            del data['links']['%s.history_current' % resource]

        # Write to a file
        filepath = os.path.join(base_dir, '%s.json' % resource)
        with codecs.open(filepath, 'w', 'utf8') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))

    return counts

if __name__ == '__main__':
    import argparse
    description = 'Download data from API.'
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
        '-d', '--data', default='data',
        help='Output data folder (default: data)')
    args = parser.parse_args()

    # Setup logging
    verbose = args.verbose
    quiet = args.quiet
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fmat = '%(levelname)s - %(message)s'
    logger_name = 'tools'
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
    data = args.data
    if data.endswith('/'):
        data = data[:-1]
    logger.info("Downloading data from %s to %s", api, data)

    # Initialize client
    client = Client(api)

    # Load data
    counts = download_data(client, data)

    if counts:
        logger.info("Download complete.")
    else:
        logger.info("No data downloaded.")
