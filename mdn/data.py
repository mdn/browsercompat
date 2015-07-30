# coding: utf-8
"""Data lookup operations for MDN parsing."""

from collections import namedtuple

from webplatformcompat.models import (
    Feature, Section, Specification, Support, Version)
from .utils import is_new_id, normalize_name, slugify


class Data(object):
    """
    Provide data operations for MDN parsing.

    Parsing an MDN page requires loading existing data for many purposes.
    This class loads the data and, if it can, caches the data.
    """

    def __init__(self):
        self.specifications = {}
        self.subfeature_data = {}

    FeatureParams = namedtuple(
        'FeatureParams', ['feature', 'feature_id', 'slug'])

    def lookup_feature_params(self, parent_feature, name):
        """Get or create the feature ID and slug given a name.

        Return is a named tuple:
        * feature - A Feature if found, None if no existing feature
        * feature_id - The feature ID, prefixed with an underscore if new
        * slug - A unique slug for this feature
        """
        nname = normalize_name(name)

        # Initialize subfeature data as needed
        if parent_feature.id not in self.subfeature_data:
            subfeatures = {}
            for feature in Feature.objects.filter(parent=parent_feature):
                if 'zxx' in feature.name:
                    fname = feature.name['zxx']
                else:
                    fname = feature.name['en']
                fname = normalize_name(fname)
                subfeatures[fname] = self.FeatureParams(
                    feature, feature.id, feature.slug)
            self.subfeature_data[parent_feature.id] = subfeatures

        # Select the Feature ID and slug
        subfeatures = self.subfeature_data[parent_feature.id]
        if nname not in subfeatures:
            feature_id = '_' + nname
            attempt = 0
            feature_slug = None
            while not feature_slug:
                base_slug = parent_feature.slug + '_' + nname
                feature_slug = slugify(base_slug, suffix=attempt)
                if Feature.objects.filter(slug=feature_slug).exists():
                    attempt += 1
                    feature_slug = ''
            subfeatures[nname] = self.FeatureParams(
                None, feature_id, feature_slug)

        return self.subfeature_data[parent_feature.id][nname]

    def lookup_section_id(self, spec_id, subpath, locale='en'):
        """Retrieve a section ID given a Specification ID and subpath."""
        for section in Section.objects.filter(specification_id=spec_id):
            if section.subpath.get(locale) == subpath:
                return section.id
        return None

    def lookup_specification(self, mdn_key):
        """Retrieve a Specification by key."""
        if mdn_key not in self.specifications:
            try:
                spec = Specification.objects.get(mdn_key=mdn_key)
            except Specification.DoesNotExist:
                spec = None
            self.specifications[mdn_key] = spec
        return self.specifications[mdn_key]

    def lookup_support_id(self, version_id, feature_id):
        """Lookup or create a support ID for a version and feature."""
        support = None
        real_version = not is_new_id(version_id)
        real_feature = not is_new_id(feature_id)
        if real_version and real_feature:
            # Might be known version
            try:
                support = Support.objects.get(
                    version=version_id, feature=feature_id)
            except Support.DoesNotExist:
                pass
        if support:
            # Known support
            support_id = support.id
        else:
            # New support
            support_id = "_%s-%s" % (feature_id, version_id)
        return support_id

    VersionParams = namedtuple("VersionParams", ["version", "version_id"])

    def lookup_version_params(
            self, browser_id, browser_name, version_name):
        """Get or create the version ID and normalized name by version string.

        Keyword Arguments:
        * browser_id - The ID of an existing browser, or a underscore-prefixed
            string for a new browser.
        * browser_name - The name of the browser
        * version_name - The version string, such as 1.0, 'current', or
            'nightly'

        Return is a named tuple:
        * version - A Version if found, None if no existing version
        * version_id - The version ID, prefixed with an underscore if new
        """
        version = None
        if not is_new_id(browser_id):
            # Might be known version
            try:
                version = Version.objects.get(
                    browser=browser_id, version=version_name)
            except Version.DoesNotExist:
                pass
        if version:
            # Known version
            version_id = version.id
        else:
            # New version
            version_id = "_%s-%s" % (browser_name, version_name)

        return self.VersionParams(version, version_id)
