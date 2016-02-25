"""Scrape data from MDN pages into API format."""
from __future__ import unicode_literals
from collections import OrderedDict
from itertools import chain

from django.utils.six import text_type
from parsimonious import IncompleteParseError
from webplatformcompat.models import (
    Browser, Feature, Reference, Section, Specification, Support, Version)

from .compatibility import CompatSectionExtractor
from .data import Data
from .html import HnElement
from .kumascript import kumascript_grammar, KumaVisitor
from .specifications import SpecSectionExtractor
from .utils import date_to_iso, is_new_id
from .visitor import Extractor


def scrape_feature_page(feature_page):
    """Scrape a FeaturePage object, which links an API Feature to an MDN page.

    1. Data and data issues are extracted from the English raw page using
       scrape_page(). The page is fetched with the MDN ?raw API call, such as
       https://developer.mozilla.org/en-US/docs/Web/API/CSSMediaRule?raw
    2. ScrapedViewFeature converts the data into the 'view_feature' format used
       by the API, with additions for issues and scrape metadata, and
    3. The formatted data is stored in the FeaturePage.data field.
    """
    en_content = feature_page.translatedcontent_set.get(locale='en-US')
    scraped_data = scrape_page(en_content.raw, feature_page.feature)
    view_feature = ScrapedViewFeature(feature_page, scraped_data)
    merged_data = view_feature.generate_data()

    # Add issues
    for issue in scraped_data['issues']:
        feature_page.add_issue(issue, 'en-US')
    merged_data['meta']['scrape']['issues'] = (
        feature_page.data['meta']['scrape']['issues'])

    # Update status, issues
    has_data = (scraped_data['specs'] or scraped_data['compat'] or
                scraped_data['issues'])
    if has_data:
        if feature_page.critical:
            feature_page.status = feature_page.STATUS_PARSED_CRITICAL
        elif feature_page.errors:
            feature_page.status = feature_page.STATUS_PARSED_ERROR
        elif feature_page.warnings:
            feature_page.status = feature_page.STATUS_PARSED_WARNING
        else:
            feature_page.status = feature_page.STATUS_PARSED
    else:
        feature_page.status = feature_page.STATUS_NO_DATA
    merged_data['meta']['scrape']['phase'] = feature_page.get_status_display()

    # Is compatibility table converted?
    embedded_compat = scraped_data['embedded_compat']
    if embedded_compat:
        if feature_page.feature.slug in embedded_compat:
            feature_page.converted_compat = feature_page.CONVERTED_YES
        else:
            feature_page.converted_compat = feature_page.CONVERTED_MISMATCH
    elif has_data:
        feature_page.converted_compat = feature_page.CONVERTED_NO
    else:
        feature_page.converted_compat = feature_page.CONVERTED_NO_DATA

    # Is compatibility table comitted to the API?
    if feature_page.status in (
            feature_page.STATUS_PARSED,
            feature_page.STATUS_PARSED_WARNING):
        feature_page.committed = feature_page.COMMITTED_YES
        has_new_items = False
        has_old_items = False
        for resource_type in ('supports', 'features', 'sections'):
            for resource in merged_data['linked'][resource_type]:
                if is_new_id(resource['id']):
                    has_new_items = True
                else:
                    has_old_items = True
        if has_new_items:
            if has_old_items:
                feature_page.committed = feature_page.COMMITTED_NEEDS_UPDATE
            else:
                feature_page.committed = feature_page.COMMITTED_NO
        elif has_old_items:
            feature_page.committed = feature_page.COMMITTED_YES
        else:
            feature_page.committed = feature_page.COMMITTED_NO_DATA
    elif has_data:
        feature_page.committed = feature_page.COMMITTED_NEEDS_FIXES
    else:
        feature_page.committed = feature_page.COMMITTED_NO_DATA

    feature_page.data = merged_data
    feature_page.save()


def scrape_page(mdn_page, feature, locale='en', data=None):
    """Find data and data issues in an MDN feature page.

    If the page appears to have relevant data, it is:
    1. Parsed with the kumascript_grammar,
    2. Processed with the PageVisitor into HTMLIntervals
    3. Data and data issues are extracted and packaged with PageExtractor
    """
    no_data = OrderedDict((
        ('locale', locale),
        ('specs', []),
        ('compat', []),
        ('footnotes', None),
        ('issues', []),
        ('embedded_compat', None),
    ))

    # Quick check for data in page
    if not (
            ('Browser compatibility</h' in mdn_page) or
            ('Specifications</h' in mdn_page) or
            ('CompatibilityTable' in mdn_page)):
        return no_data

    # Parse the page with HTML + KumaScript grammar

    try:
        page_parsed = kumascript_grammar.parse(mdn_page)
    except IncompleteParseError as ipe:
        narrow_pos, narrow_end = narrow_parse_error(mdn_page, ipe.pos)
        no_data['issues'].append(('halt_import', narrow_pos, narrow_end, {}))
        return no_data

    # Convert parsed page and extract data
    data = data or Data()
    elements = PageVisitor(data=data).visit(page_parsed)
    extractor = PageExtractor(
        elements=elements, feature=feature, locale=locale, data=data)
    page_data = extractor.extract()
    return page_data


def narrow_parse_error(fragment, pos):
    """Try to narrow parse errors to inner elements.

    Return is a tuple:
    - start - The probable start position of the error
    - end - The probable end position of the error
    """
    default = pos, len(fragment)
    if fragment[pos] != '<':
        # Not an element error - mark rest of fragment
        return default

    # Determine outer tags
    try:
        end = fragment.index('>', pos)
    except ValueError:
        return default
    try:
        ws_start = fragment.index(' ', pos)
    except ValueError:
        ws_start = end + 1
    if ws_start < end:
        tag = fragment[pos:ws_start] + '>'
    else:
        tag = fragment[pos:(end + 1)]
    end_tag = tag.replace('<', '</')
    try:
        end_index = fragment.index(end_tag, pos)
    except ValueError:
        # Can't find end tag - mark rest of fragment
        return default
    else:
        # Try parsing the content inside the tags
        subfragment = fragment[(end + 1):end_index]
        try:
            kumascript_grammar.parse(subfragment)
        except IncompleteParseError as ipe:
            if ipe.pos:
                # Narrow down to an inner tag
                subpos, subend = narrow_parse_error(subfragment, ipe.pos)
                return subpos + end + 1, subend + end + 1
            else:
                # Mark all inner content as issue
                return end + 1, end_index
        else:
            # Inner parses - the tag is the problem
            return pos, end_index + len(end_tag)


class PageVisitor(KumaVisitor):
    """Converts a parsed MDN page into HTML and text elements.

    Uses most of KumaVisitor behaviour, except defaults to allowing all
    HTML element attributes, leaving validation to section-specific extractors.
    """

    _default_attribute_actions = {None: 'keep'}


class PageExtractor(Extractor):
    """Collects elements into sections and extracts relevant data.

    Split elements into sections by header elements (<h2>, <h3>, etc.).
    Looks for the Specifications and Browser Compatibility sections, and
    passes the sections to specialized extractors to find data and record
    issues.
    """

    def __init__(self, feature, locale='en', **kwargs):
        self.feature = feature
        self.locale = locale
        self.initialize_extractor(**kwargs)

    def setup_extract(self):
        """Initialize the extractor."""
        self.previous_section = None
        self.section = []
        self.specs = []
        self.compat = []
        self.footnotes = OrderedDict()
        self.embedded_compat = []

    def entering_element(self, state, element):
        """Extract and change state when entering an element.

        Return is a tuple:
        - The next state
        - True if the child elements should be walked, False if
          already processed or can be skipped.
        """
        if state == 'begin':
            if isinstance(element, HnElement):
                self.section.append(element)
                return 'in_section', False
            else:
                return 'begin', False
        elif state == 'in_section':
            if isinstance(element, HnElement):
                self.process_current_section()
                self.section.append(element)  # Start new section
            else:
                self.section.append(element)
            return 'in_section', False
        else:  # pragma: no cover
            raise Exception('Unexpected state "{}"'.format(state))

    def leaving_element(self, state, element):
        """No state changes on leaving elements."""
        return state

    def extracted_data(self):
        """Finalize and return extracted data."""
        if self.section:
            self.process_current_section()
        if not (self.specs or self.compat or self.issues):
            self.add_issue('no_data', self.elements[0])
        return OrderedDict((
            ('locale', self.locale),
            ('specs', self.specs),
            ('compat', self.compat),
            ('issues', self.issues),
            ('footnotes', self.footnotes or None),
            ('embedded_compat', self.embedded_compat or None),
        ))

    def process_current_section(self):
        """Process complete, relevant sections with specific Extractors."""
        header = self.section[0]
        if header.to_text().lower() in ('specification', 'specifications'):
            extractor = SpecSectionExtractor(
                elements=self.section, data=self.data)
            extracted = extractor.extract()
            self.specs.extend(extracted['specs'])
            self.issues.extend(extracted['issues'])
        elif header.to_text().lower() == 'browser compatibility':
            extractor = CompatSectionExtractor(
                elements=self.section, feature=self.feature, data=self.data)
            extracted = extractor.extract()
            self.compat.extend(extracted['compat_divs'])
            self.footnotes.update(extracted['footnotes'])
            self.issues.extend(extracted['issues'])
            self.embedded_compat.extend(extracted['embedded'])

        # Should this become the new "previous section"?
        # If the same level (<h2> vs previous <h2>), yes
        # If a higher level (<h1> vs previous <h2>), yes
        # If a lower level (<h3> vs previous <h2>, no, but check if it's a
        #   documentation section after a Browser Compatibility section, to
        #   warn about lost data.
        replace_section = True
        if self.previous_section:
            if header.level > self.previous_section[0].level:
                replace_section = False
                prev_title = self.previous_section[0].to_text().lower()
                is_browser_compat = prev_title == 'browser compatibility'
                if is_browser_compat:
                    title = header.to_text()
                    self.add_issue('skipped_h3', header, h3=title)
        if replace_section:
            self.previous_section = self.section
        self.section = []


class ScrapedViewFeature(object):
    """Combine a scraped MDN page with existing API data.

    This code scrapes data from the English features pages. It merge new
    scraped data with existing API data.

    Further work is needed to scrape pages in non-English languages, but it is
    doubtful this will be a high priority.  Translators may need to redo work
    inside the new contribution interface.
    """

    tab_name = {
        'desktop': 'Desktop Browsers',
        'mobile': 'Mobile Browsers',
    }

    def __init__(self, feature_page, scraped_data):
        self.feature_page = feature_page
        self.feature = feature_page.feature
        self.scraped_data = scraped_data
        self.resources = OrderedDict()
        for resource_type in (
                'specifications', 'maturities', 'sections', 'browsers',
                'versions', 'features', 'supports', 'references'):
            self.resources[resource_type] = OrderedDict()
        self.tabs = []
        self.compat_table_supports = OrderedDict(
            ((text_type(self.feature.id), {}),))
        self.notes = OrderedDict()

    def generate_data(self):
        """Combine the page and scraped data into view_feature structure."""
        fp_data = self.feature_page.reset_data()

        for spec_row in self.scraped_data['specs']:
            self.load_specification_row(spec_row)
        for table in self.scraped_data['compat']:
            self.load_compat_table(table)

        # Set linked resources
        for resource_type, resources in self.resources.items():
            fp_data['linked'][resource_type] = self.sort_values(resources)

        # Set relations on subject feature
        main_id = str(self.feature.id)
        fp_data['features']['links']['children'] = list(
            f_id for f_id in self.compat_table_supports.keys()
            if f_id != main_id)
        fp_data['features']['links']['references'] = list(
            reference['id'] for reference in fp_data['linked']['references']
            if reference['links']['feature'] == main_id)
        fp_data['features']['links']['supports'] = sorted(
            support['id'] for support in fp_data['linked']['supports']
            if support['links']['feature'] == main_id)

        # Set view_feature metadata
        languages = fp_data['features']['mdn_uri'].keys()
        fp_data['meta']['compat_table']['languages'] = list(languages)
        fp_data['meta']['compat_table']['tabs'] = self.tabs
        fp_data['meta']['compat_table']['supports'] = (
            self.compat_table_supports)
        fp_data['meta']['compat_table']['notes'] = self.notes

        return fp_data

    def load_specification_row(self, spec_row):
        """Load Specification, Maturity, and Section."""
        # Load Specification and Maturity
        if spec_row['specification.id']:
            spec_content, mat_content = self.load_specification(
                spec_row['specification.id'])
        else:
            spec_content, mat_content = self.new_specification(spec_row)
        self.add_resource('specifications', spec_content)
        self.add_resource('maturities', mat_content)

        # Load Specification Section
        if spec_row['section.id']:
            section_content = self.load_section(spec_row['section.id'])
            # TODO: bug 1251252 - empty name, subpath is None
            section_content['name']['en'] = spec_row['section.name']
            section_content['subpath']['en'] = spec_row['section.subpath']
        else:
            section_content = self.new_section(spec_row, spec_content['id'])
        self.add_resource('sections', section_content)

        # Load Reference
        reference_content = self.load_or_new_reference(section_content['id'])
        if spec_row['section.note']:
            reference_content['note']['en'] = spec_row['section.note']
        else:
            reference_content['note'] = None
        self.add_resource('references', reference_content)

    def load_compat_table(self, table):
        """Load a compat table."""
        tab = OrderedDict((
            ('name',
             {'en': self.tab_name.get(table['name'], 'Other Environments')}),
            ('browsers', []),
        ))
        # Load Browsers (first row)
        for browser_entry in table['browsers']:
            if is_new_id(browser_entry['id']):
                browser_content = self.new_browser(browser_entry)
            else:
                browser_content = self.load_browser(browser_entry['id'])
            self.add_resource('browsers', browser_content)
            tab['browsers'].append(text_type(browser_content['id']))

        # Load Features (first column)
        for feature_entry in table['features']:
            if is_new_id(feature_entry['id']):
                feature_content = self.new_feature(feature_entry)
            else:
                feature_content = self.load_feature(feature_entry['id'])
            if text_type(feature_entry['id']) != text_type(self.feature.id):
                self.add_resource_if_new('features', feature_content)
            self.compat_table_supports.setdefault(
                text_type(feature_content['id']), OrderedDict())

        # Load Versions (explicit or implied in cells)
        for version_entry in table['versions']:
            if is_new_id(version_entry['id']):
                version_content = self.new_version(version_entry)
            else:
                version_content = self.load_version(version_entry['id'])
            self.add_resource_if_new('versions', version_content)

        # Load Supports (cells)
        for support_entry in table['supports']:
            if is_new_id(support_entry['id']):
                support_content = self.new_support(support_entry)
            else:
                support_content = self.load_support(support_entry['id'])
            support = self.add_resource_if_new('supports', support_content)
            feature_id = support_content['links']['feature']
            if text_type(feature_id) != text_type(self.feature.id):
                # Subject feature supports are populated in generate_data
                feature = self.resources['features'][feature_id]
                if support['id'] not in feature['links']['supports']:
                    feature['links']['supports'].append(support['id'])

            if support_content['note']:
                note_id = len(self.notes) + 1
                self.notes[support_content['id']] = note_id

            # Set the meta lookup
            version = self.get_resource(
                'versions', support_content['links']['version'])
            feature_id = support_content['links']['feature']
            browser_id = version['links']['browser']
            supports = self.compat_table_supports[feature_id]
            supports.setdefault(browser_id, [])
            supports[browser_id].append(support_entry['id'])
        self.tabs.append(tab)

    def add_resource(self, resource_type, content):
        """Add a linked resource, replacing any existing resource."""
        resource_id = content['id']
        self.resources[resource_type][resource_id] = content

    def add_resource_if_new(self, resource_type, content):
        """Add a linked resource only if there is no existing resource."""
        resource_id = content['id']
        return self.resources[resource_type].setdefault(resource_id, content)

    def get_resource(self, resource_type, resource_id):
        """Get an existing linked resource."""
        return self.resources[resource_type][resource_id]

    def sort_values(self, d):
        """Return dictionary values, sorted by keys."""
        existing_keys = sorted([k for k in d.keys() if not is_new_id(k)])
        new_keys = sorted([k for k in d.keys() if is_new_id(k)])
        return list(d[k] for k in chain(existing_keys, new_keys))

    def load_specification(self, spec_id):
        """Serialize an existing specification."""
        spec = Specification.objects.get(id=spec_id)
        spec_content = OrderedDict((
            ('id', text_type(spec_id)),
            ('slug', spec.slug),
            ('mdn_key', spec.mdn_key),
            ('name', spec.name),
            ('uri', spec.uri),
            ('links', OrderedDict((
                ('maturity', text_type(spec.maturity_id)),
            )))))
        mat = spec.maturity
        mat_content = OrderedDict((
            ('id', text_type(mat.id)),
            ('slug', mat.slug),
            ('name', mat.name)))
        return spec_content, mat_content

    def new_specification(self, spec_row):
        """Serialize a new specification."""
        spec_id = '_' + spec_row['specification.mdn_key']
        mat_id = '_unknown'
        spec_content = OrderedDict((
            ('id', spec_id),
            ('mdn_key', spec_row['specification.mdn_key']),
            ('links', OrderedDict((
                ('maturity', mat_id),
            )))))
        mat_content = self.add_resource_if_new(
            'maturities', OrderedDict((
                ('id', mat_id),
                ('slug', ''),
                ('name', {'en': 'Unknown'}),
                ('links', {'specifications': []}))))
        return spec_content, mat_content

    def load_section(self, section_id):
        """Serialize an existing section."""
        section = Section.objects.get(id=section_id)
        section_content = OrderedDict((
            ('id', text_type(section_id)),
            ('number', section.number or None),
            ('name', section.name),
            ('subpath', section.subpath),
            ('links', OrderedDict((
                ('specification', text_type(section.specification_id)),)))))
        return section_content

    def new_section(self, spec_row, spec_id):
        """Serialize a new section."""
        section_id = (
            '_' + text_type(spec_id) + '_' + spec_row['section.subpath'])
        section_content = OrderedDict((
            ('id', section_id),
            ('number', None),
            ('name', OrderedDict()),
            ('subpath', OrderedDict()),
            ('links', OrderedDict((
                ('specification', text_type(spec_id)),)))))
        section_content['name']['en'] = spec_row['section.name']
        section_content['subpath']['en'] = spec_row['section.subpath']
        return section_content

    def load_browser(self, browser_id):
        """Serialize an existing browser."""
        browser = Browser.objects.get(id=browser_id)
        browser_content = OrderedDict((
            ('id', text_type(browser.id)),
            ('slug', browser.slug),
            ('name', browser.name),
            ('note', browser.note or None),
        ))
        return browser_content

    def new_browser(self, browser_entry):
        """Serialize a new browser."""
        browser_content = OrderedDict((
            ('id', browser_entry['id']),
            ('slug', ''),
            ('name', {'en': browser_entry['name']}),
            ('note', None),
        ))
        return browser_content

    def load_feature(self, feature_id):
        """Serialize an existing feature."""
        feature = Feature.objects.get(id=feature_id)
        reference_ids = [
            text_type(r_id) for r_id in
            feature.references.values_list('pk', flat=True)]
        support_ids = [
            text_type(s_id) for s_id in
            sorted(feature.supports.values_list('pk', flat=True))]
        parent_id = (
            text_type(feature.parent_id) if feature.parent_id
            else None)
        children_ids = [
            text_type(c_id) for c_id in
            feature.children.values_list('pk', flat=True)]
        feature_content = OrderedDict((
            ('id', text_type(feature_id)),
            ('slug', feature.slug),
            ('mdn_uri', feature.mdn_uri or None),
            ('experimental', feature.experimental),
            ('standardized', feature.standardized),
            ('stable', feature.stable),
            ('obsolete', feature.obsolete),
            ('name', feature.name),
            ('links', OrderedDict((
                ('references', reference_ids),
                ('supports', support_ids),
                ('parent', parent_id),
                ('children', children_ids))))))
        if list(feature.name.keys()) == ['zxx']:
            feature_content['name'] = feature.name['zxx']
        return feature_content

    def new_feature(self, feature_entry):
        """Serialize a new feature."""
        if feature_entry.get('canonical'):
            fname = feature_entry['name']
        else:
            fname = {'en': feature_entry['name']}
        feature_content = OrderedDict((
            ('id', feature_entry['id']),
            ('slug', feature_entry['slug']),
            ('mdn_uri', None),
            ('experimental', feature_entry.get('experimental', False)),
            ('standardized', feature_entry.get('standardized', True)),
            ('stable', feature_entry.get('stable', True)),
            ('obsolete', feature_entry.get('obsolete', False)),
            ('name', fname),
            ('links', OrderedDict((
                ('references', []),
                ('supports', []),
                ('parent', text_type(self.feature.id)),
                ('children', []))))))
        return feature_content

    def load_version(self, version_id):
        """Serialize an existing version."""
        version = Version.objects.get(id=version_id)
        version_content = OrderedDict((
            ('id', text_type(version.id)),
            ('version', version.version or None),
            ('release_day', date_to_iso(version.release_day)),
            ('retirement_day', date_to_iso(version.retirement_day)),
            ('status', version.status),
            ('release_notes_uri', version.release_notes_uri or None),
            ('note', version.note or None),
            ('order', version._order),
            ('links', OrderedDict((
                ('browser', text_type(version.browser_id)),)))))
        return version_content

    def new_version(self, version_entry):
        """Serialize a new version."""
        version = version_entry['version']
        status = 'unknown'
        if version == 'nightly':
            status = 'future'
        elif not version:
            version = 'current'
            status = 'current'
        version_content = OrderedDict((
            ('id', version_entry['id']),
            ('version', version),
            ('release_day', None),
            ('retirement_day', None),
            ('status', status),
            ('release_notes_uri', None),
            ('note', None),
            ('links', OrderedDict((
                ('browser', text_type(version_entry['browser'])),)))))
        return version_content

    def load_support(self, support_id):
        """Serialize an existing support."""
        support = Support.objects.get(id=support_id)
        support_content = OrderedDict((
            ('id', text_type(support.id)),
            ('support', support.support),
            ('prefix', support.prefix or None),
            ('prefix_mandatory', support.prefix_mandatory),
            ('alternate_name', support.alternate_name or None),
            ('alternate_mandatory', support.alternate_mandatory),
            ('requires_config', support.requires_config or None),
            ('default_config', support.default_config or None),
            ('protected', support.protected),
            ('note', support.note or None),
            ('links', OrderedDict((
                ('version', text_type(support.version_id)),
                ('feature', text_type(support.feature_id)))))))
        return support_content

    def new_support(self, support_entry):
        """Serialize a new support."""
        support_content = OrderedDict((
            ('id', support_entry['id']),
            ('support', support_entry['support']),
            ('prefix', support_entry.get('prefix')),
            ('prefix_mandatory', bool(support_entry.get('prefix', False))),
            ('alternate_name', support_entry.get('alternate_name')),
            ('alternate_mandatory',
                support_entry.get('alternate_mandatory', False)),
            ('requires_config', support_entry.get('requires_config')),
            ('default_config', support_entry.get('default_config')),
            ('protected', support_entry.get('protected', False)),
            ('note', None),
            ('links', OrderedDict((
                ('version', text_type(support_entry['version'])),
                ('feature', text_type(support_entry['feature'])))))))
        if support_entry.get('footnote'):
            support_content['note'] = {'en': support_entry['footnote']}
        return support_content

    def load_or_new_reference(self, section_id):
        try:
            reference = Reference.objects.get(
                feature_id=self.feature.id, section_id=section_id)
        except (Reference.DoesNotExist, ValueError):
            reference_content = OrderedDict((
                ('id', '_%s_%s' % (self.feature.id, section_id)),
                ('note', OrderedDict()),
                ('links', OrderedDict((
                    ('feature', text_type(self.feature.id)),
                    ('section', text_type(section_id)))))))
        else:
            reference_content = OrderedDict((
                ('id', text_type(reference.id)),
                ('note', reference.note),
                ('links', OrderedDict((
                    ('feature', text_type(reference.feature_id)),
                    ('section', text_type(reference.section_id)))))))
        return reference_content
