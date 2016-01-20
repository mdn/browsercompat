#!/usr/bin/env python
"""Import features from MDN.

For each Feature in the API, run the importer to re-parse the MDN page for
compatibility data. This can work with the last fetched copy of the MDN page,
or re-download all the MDN pages.

This will not detect new MDN pages - see mirror_mdn_features.py. It will take
hours to run, even on a fast connection.
"""

import time

from requests import RequestException

from common import Tool
from resources import Collection


class ImportMDNData(Tool):
    """Import features from MDN, or reparse imported features."""

    logger_name = 'tools.import_mdn'
    parser_options = ['api', 'user', 'password']

    def get_parser(self):
        parser = super(ImportMDNData, self).get_parser()
        parser.add_argument(
            '--reparse', action='store_true',
            help='Re-parse cached pages instead of downloading fresh')
        return parser

    def run(self, rate=5, *args, **kwargs):
        self.login()
        collection = Collection(self.client)
        collection.load_all('features')

        # Collect feature URIs
        uris = []
        for feature in collection.get_resources('features'):
            if feature.mdn_uri and feature.mdn_uri.get('en'):
                uris.append((feature.mdn_uri['en'], feature.id.id))
        total = len(uris)
        if self.reparse:
            action = 'Reparsing cached pages...'
        else:
            action = 'Reparsing latest pages...'
        self.logger.info(
            'Features loaded, %d MDN pages found. %s', total, action)

        # Import from MDN, with rate limiting
        start_time = time.time()
        mdn_requests = 0
        counts = {'new': 0, 'reset': 0, 'reparsed': 0, 'unchanged': 0}
        log_at = 15
        logged_at = time.time()
        for uri, feature_id in uris:
            attempt = 1
            max_attempt = 3
            while attempt <= max_attempt:
                if attempt > 1:
                    self.logger.info(
                        'Attempt %d of %d for %s', attempt, max_attempt, uri)
                try:
                    import_type = self.import_page(uri, feature_id)
                except RequestException as exception:
                    if attempt < max_attempt:
                        self.logger.error('%s', exception)
                        self.logger.info('Pausing 5 seconds...')
                        time.sleep(5)
                    else:
                        self.logger.info('Giving up on %s.', uri)
                    attempt += 1
                else:
                    counts[import_type] += 1
                    if import_type in ('new', 'reset'):
                        mdn_requests += 1
                    break

            # Pause for rate limiting?
            current_time = time.time()
            if rate:
                elapsed = current_time - start_time
                target = start_time + float(mdn_requests) / rate
                current_rate = float(mdn_requests) / elapsed
                if time.time < target:
                    rest = int(target - current_time) + 1
                    self.logger.warning(
                        '%d pages fetched, %0.2f per second, target rate %d'
                        ' per second.  Resting %d seconds.',
                        mdn_requests, current_rate, rate, rest)
                    time.sleep(rest)
                    logged_at = time.time()
                    current_time = time.time()

            # Log progress?
            if (logged_at + log_at) < current_time:
                processed = sum(counts.values())
                percent = int(100 * (float(processed) / total))
                self.logger.info(
                    '  Processed %d of %d MDN pages (%d%%)...',
                    processed, total, percent)
                logged_at = current_time

        return counts

    def import_page(self, uri, feature_id):
        """Import an MDN page."""
        importer_search = self.api + '/importer/search'
        response = self.client.session.get(
            importer_search, params={'url': uri})
        if 'importer/create?' in response.url:
            self.logger.info('Fetching %s...', uri)
            create_url = response.url
            csrf = self.client.session.cookies['csrftoken']
            params = {
                'url': uri,
                'feature': feature_id,
                'csrfmiddlewaretoken': csrf,
            }
            response = self.client.session.post(create_url, params)
            return 'new'
        else:
            response.raise_for_status()
            obj_url = response.url
            assert '/importer/' in obj_url
            if self.reparse:
                action_url = obj_url + '/reparse'
                import_type = 'reparsed'
            else:
                action_url = obj_url + '/reset'
                import_type = 'reset'
            csrf = self.client.session.cookies['csrftoken']
            params = {'csrfmiddlewaretoken': csrf}
            response = self.client.session.post(action_url, params)
            return import_type


if __name__ == '__main__':
    tool = ImportMDNData()
    tool.init_from_command_line()
    tool.logger.info('Loading data into {tool.api}'.format(tool=tool))
    counts = tool.run()

    if counts:
        tool.logger.info('Import complete. Counts:')
        c_new = counts.get('new', 0)
        c_reset = counts.get('reset', 0)
        c_reparsed = counts.get('reparsed', 0)
        c_unchanged = counts.get('unchanged', 0)
        c_text = []
        if c_new:
            c_text.append('%d new' % c_new)
        if c_reset:
            c_text.append('%d reset' % c_reset)
        if c_reparsed:
            c_text.append('%d reparsed' % c_reparsed)
        if c_unchanged:
            c_text.append('%d unchanged' % c_unchanged)
        if c_text:
            tool.logger.info(', '.join(c_text))
    else:
        tool.logger.info('No data uploaded.')
