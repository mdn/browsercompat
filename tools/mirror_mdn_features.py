#!/usr/bin/env python
"""Crawl subset of MDN pages, creating and updating API Features.

The subset is defined in the current_mdn_uris, and includes most pages found
to have Browser Compatibility tables. Due to the effort to remove Zones, some
of subset may no longer be on MDN.

"Standard" usage is:

tools/mirror_mdn_features.py --no-cache --skip-deletes

This downloads fresh copies of MDN pages, and skips deleting resources for
removed or renamed pages. This will take 1-2 hours to run, even on a fast
connection.
"""

from __future__ import print_function

from cgi import escape
from json import loads
from string import lowercase
import os.path
import time

from requests.exceptions import HTTPError

from common import Tool
from resources import Collection, Feature


class MirrorMDNFeatures(Tool):
    """Create and Update API features for MDN pages."""

    logger_name = 'tools.mirror_mdn_features'
    parser_options = ['api', 'user', 'password', 'data', 'nocache']
    base_mdn_domain = 'https://developer.mozilla.org'
    base_mdn_uri = base_mdn_domain + '/en-US/docs/'

    def __init__(self, *args, **kwargs):
        super(MirrorMDNFeatures, self).__init__(*args, **kwargs)
        self.rate_limit_start = time.time()
        self.rate_limit_requests = 0

    def get_parser(self):
        parser = super(MirrorMDNFeatures, self).get_parser()
        parser.add_argument(
            '--skip-deletes', action='store_true',
            help='Skip deleting API resources')
        return parser

    def run(self, *args, **kwargs):
        self.login()
        api_collection = Collection(self.client)
        self.logger.info('Reading existing features from API')
        api_collection.load_all('features')

        # Copy feature to working local collection
        local_collection = Collection()
        local_collection.load_collection(api_collection)
        features = self.known_features(local_collection)
        feature_by_uri = dict((k[0], k[2]) for k in features)
        feature_by_slug = dict((k[1], k[2]) for k in features)
        slugs = set(feature_by_slug.keys())

        cache_state = 'using cache' if self.use_cache else 'no cache'
        self.logger.info('Reading pages from MDN (%s)', cache_state)
        mdn_uris = self.current_mdn_uris()

        # Find new / updated pages
        new_page, needs_url, existing_page = 0, 0, 0
        seen_uris = set()
        for path, parent_path, raw_slug, title in mdn_uris:
            uri = self.base_mdn_domain + path
            seen_uris.add(uri)
            feature = feature_by_uri.get(uri)
            if feature:
                existing_page += 1
                feature.name = self.to_trans(title)
            else:
                slug = self.unique_slugify(raw_slug, slugs)
                feature = feature_by_slug.get(slug)
                if feature:
                    # Need to add URI to feature
                    feature.mdn_uri = {'en': uri}
                    feature_by_uri[uri] = feature
                    needs_url += 1
                else:
                    if parent_path:
                        parent_uri = self.base_mdn_domain + parent_path
                        parent_feature = feature_by_uri.get(parent_uri)
                        assert parent_feature,\
                            'No feature for parent page {}'.format(parent_uri)
                        parent_id = parent_feature.id.id
                    else:
                        parent_id = None
                    feature = Feature(
                        id='_' + slug, slug=slug, mdn_uri={'en': uri},
                        name=self.to_trans(title), parent=parent_id)
                    local_collection.add(feature)
                    feature_by_uri[uri] = feature
                    feature_by_slug[slug] = feature
        self.logger.info(
            'MDN URIs gathered, %d found (%d new, %d needs url, %d existing).',
            len(mdn_uris), new_page, needs_url, existing_page)

        # Find deleted pages
        for uri, feature in feature_by_uri.items():
            if uri and uri not in seen_uris:
                local_collection.remove(feature)

        return self.sync_changes(
            api_collection, local_collection, self.skip_deletes)

    def to_trans(self, text):
        """Convert text to an API translatable string.

        If it looks canonical, convert to display in a <code></code> tag.
        If it looks like English, convert to display in <div></div> tag.
        """
        if ' ' in text:
            canonical = False
        elif text[0] in lowercase:
            canonical = True
        elif text[0] == '<' and text[-1] == '>':
            canonical = True
        elif text[0] == ':':
            canonical = True
        elif text[0].endswith('()'):
            canonical = True
        else:
            canonical = False
        if canonical:
            return escape(text)
        else:
            return {'en': escape(text)}

    def current_mdn_uris(self):
        """Load potential URIs from MDN."""
        base_paths = [
            'Web', 'Navigation_timing', 'Server-sent_events', 'WebAPI',
            'WebSockets']

        data = []
        for base_path in base_paths:
            data.extend(self.crawl_mdn(base_path))
        return data

    def crawl_mdn(self, path, parent_path=None, attempt=0):
        """Recursively crawl MDN paths."""
        cache_file = os.path.join('mdn_children', path + '.json')
        mdn_uri = self.base_mdn_uri + path
        children_uri = mdn_uri + '$children?depth=1'
        headers = {'Accept': 'application/json'}
        try:
            children_data = self.cached_download(
                cache_file, children_uri, headers=headers, retries=60)
        except HTTPError as e:
            self.logger.error('Error downloading %s: %s', children_uri, e)
            return []

        try:
            mdn_json = loads(children_data)
        except ValueError as e:
            self.logger.error(
                'Unable to decode JSON in %s: %s', cache_file, e)
            if attempt < 3:
                os.remove(cache_file)
                return self.crawl_mdn(path, parent_path, attempt + 1)
            else:
                raise
        if mdn_json and 'url' in mdn_json:
            path = mdn_json['url']
            title = mdn_json['title']
            slug = mdn_json['slug']
            data = [(path, parent_path, slug, title)]
            for subjson in mdn_json['subpages']:
                subslug = subjson['slug']
                if subslug.endswith('/'):
                    # /en-US/docs/Web/Events/onconnected redirected
                    self.logger.warning('Invalid slug for %s', subjson)
                else:
                    data.extend(self.crawl_mdn(subslug, parent_path=path))
            return data
        elif mdn_json:
            self.logger.warning('Bad JSON %s', mdn_json)
        else:
            self.logger.warning('No data at %s', path)
        return []

    def known_features(self, collection):
        """Load URIs from collection's features."""
        uris = []
        for feature in collection.get_resources('features'):
            uri = feature.mdn_uri and feature.mdn_uri.get('en')
            slug = feature.slug
            uris.append((uri, slug, feature))
        return uris


if __name__ == '__main__':
    tool = MirrorMDNFeatures()
    tool.init_from_command_line()
    tool.logger.info('Loading data into {tool.api}...'.format(tool=tool))
    changes = tool.run()
    tool.report_changes(changes)
