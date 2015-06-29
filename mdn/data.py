# coding: utf-8
"""Data lookup operations for MDN parsing."""

from collections import namedtuple

from webplatformcompat.models import Feature, Specification
from .utils import normalize_name, slugify


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

    def feature_params_by_name(self, parent_feature, name):
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

    def specification_by_key(self, mdn_key):
        """Retrieve a Specification by key."""
        if mdn_key not in self.specifications:
            try:
                spec = Specification.objects.get(mdn_key=mdn_key)
            except Specification.DoesNotExist:
                spec = None
            self.specifications[mdn_key] = spec
        return self.specifications[mdn_key]
