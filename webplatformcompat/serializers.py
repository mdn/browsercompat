# -*- coding: utf-8 -*-
"""API Serializers"""

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    # py26 doesn't get ordered dicts
    OrderedDict = dict

from django.db.models import CharField
from django.contrib.auth.models import User
from drf_cached_instances.models import CachedQueryset
from rest_framework.serializers import (
    DateField, DateTimeField, IntegerField, ModelSerializer,
    PrimaryKeyRelatedField, SerializerMethodField, ValidationError)

from . import fields
from .cache import Cache
from .drf_fields import (
    AutoUserField, CurrentHistoryField, HistoricalObjectField, HistoryField,
    MPTTRelationField, OptionalCharField, OptionalIntegerField,
    TranslatedTextField)
from .history import Changeset
from .models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)


#
# "Regular" Serializers
#

class WriteRestrictedOptions(ModelSerializer._options_class):
    def __init__(self, meta):
        super(WriteRestrictedOptions, self).__init__(meta)
        self.update_only_fields = getattr(meta, 'update_only_fields', ())
        self.write_once_fields = getattr(meta, 'write_once_fields', ())


class WriteRestrictedMixin(object):
    _options_class = WriteRestrictedOptions

    def get_fields(self):
        """Add read_only flag for write-restricted fields"""
        fields = super(WriteRestrictedMixin, self).get_fields()
        view = self.context.get('view', None)

        if view and view.action in ('list', 'create'):
            update_only_fields = getattr(self.opts, 'update_only_fields', [])
            for field_name in update_only_fields:
                fields[field_name].read_only = True

        if view and view.action in ('update', 'partial_update'):
            write_once_fields = getattr(self.opts, 'write_once_fields', [])
            for field_name in write_once_fields:
                fields[field_name].read_only = True

        return fields


class FieldMapMixin(object):
    """Automatically handle fields used by this project"""
    field_mapping = ModelSerializer.field_mapping
    field_mapping[fields.TranslatedField] = TranslatedTextField
    field_mapping[CharField] = OptionalCharField

    def get_field(self, model_field):
        field = super(FieldMapMixin, self).get_field(model_field)
        if isinstance(field, TranslatedTextField):
            field.allow_canonical = model_field.allow_canonical
        return field


class HistoricalModelSerializer(
        WriteRestrictedMixin, FieldMapMixin, ModelSerializer):
    """Model serializer with history manager"""

    def get_default_fields(self):
        """Add history and history_current to default fields"""
        fields = super(HistoricalModelSerializer, self).get_default_fields()

        cls = self.opts.model
        view_name = "historical%s-detail" % cls.__name__.lower()

        assert 'history' in self.opts.fields
        assert 'history' not in fields
        fields['history'] = HistoryField(view_name=view_name)

        assert 'history_current' in self.opts.fields
        assert 'history_current' not in fields
        view = self.context.get('view', None)
        read_only = view and view.action in ('list', 'create')
        fields['history_current'] = CurrentHistoryField(
            view_name=view_name, read_only=read_only)

        return fields

    def from_native(self, data, files=None):
        """If history_current in data, load historical data into instance"""
        if data and 'history_current' in data:
            history_id = int(data['history_current'])
            current_history = self.object.history.all()[0]
            if current_history.history_id != history_id:
                try:
                    historical = self.object.history.get(
                        history_id=history_id).instance
                except self.object.history.model.DoesNotExist:
                    pass
                else:
                    for field in historical._meta.fields:
                        attname = field.attname
                        hist_value = getattr(historical, attname)
                        setattr(self.object, attname, hist_value)
        return super(HistoricalModelSerializer, self).from_native(data, files)

    def validate_history_current(self, attrs, source):
        value = attrs.get(source)
        if value and self.object:
            if value.history_object.pk != self.object.id:
                raise ValidationError(
                    'history is for a different object')
        return attrs


class BrowserSerializer(HistoricalModelSerializer):
    """Browser Serializer"""

    def save_object(self, obj, **kwargs):
        if 'versions' in getattr(obj, '_related_data', {}):
            versions = obj._related_data.pop('versions')
        else:
            versions = None

        super(BrowserSerializer, self).save_object(obj, **kwargs)

        if versions:
            v_pks = [v.pk for v in versions]
            current_order = obj.get_version_order()
            if v_pks != current_order:
                obj.set_version_order(v_pks)

    class Meta:
        model = Browser
        fields = (
            'id', 'slug', 'name', 'note', 'history', 'history_current',
            'versions')
        update_only_fields = (
            'history', 'history_current', 'versions')
        write_once_fields = ('slug',)


class FeatureSerializer(HistoricalModelSerializer):
    """Feature Serializer"""

    children = MPTTRelationField(many=True, source='children')

    class Meta:
        model = Feature
        fields = (
            'id', 'slug', 'mdn_path', 'experimental', 'standardized',
            'stable', 'obsolete', 'name',
            'sections', 'supports', 'parent', 'children',
            'history_current', 'history')
        read_only_fields = ('supports',)


class MaturitySerializer(HistoricalModelSerializer):
    """Specification Maturity Serializer"""

    class Meta:
        model = Maturity
        fields = (
            'id', 'slug', 'name', 'specifications',
            'history_current', 'history')


class SectionSerializer(HistoricalModelSerializer):
    """Specification Section Serializer"""

    class Meta:
        model = Section
        fields = (
            'id', 'number', 'name', 'subpath', 'note', 'specification',
            'features', 'history_current', 'history')


class SpecificationSerializer(HistoricalModelSerializer):
    """Specification Serializer"""

    def save_object(self, obj, **kwargs):
        if 'sections' in getattr(obj, '_related_data', {}):
            sections = obj._related_data.pop('sections')
        else:
            sections = None

        super(SpecificationSerializer, self).save_object(obj, **kwargs)

        if sections:
            s_pks = [s.pk for s in sections]
            current_order = obj.get_section_order()
            if s_pks != current_order:
                obj.set_section_order(s_pks)

    class Meta:
        model = Specification
        fields = (
            'id', 'slug', 'mdn_key', 'name', 'uri', 'maturity', 'sections',
            'history_current', 'history')


class SupportSerializer(HistoricalModelSerializer):
    """Support Serializer"""

    class Meta:
        model = Support
        fields = (
            'id', 'version', 'feature', 'support', 'prefix',
            'prefix_mandatory', 'alternate_name', 'alternate_mandatory',
            'requires_config', 'default_config', 'protected', 'note',
            'footnote', 'history_current', 'history')


class VersionSerializer(HistoricalModelSerializer):
    """Browser Version Serializer"""

    order = IntegerField(read_only=True, source='_order')

    class Meta:
        model = Version
        fields = (
            'id', 'browser', 'version', 'release_day', 'retirement_day',
            'status', 'release_notes_uri', 'note', 'order',
            'supports', 'history', 'history_current')
        read_only_fields = ('supports',)


#
# Change control object serializers
#

class ChangesetSerializer(ModelSerializer):
    """Changeset Serializer"""

    user = AutoUserField()
    target_resource_type = OptionalCharField(required=False)
    target_resource_id = OptionalIntegerField(required=False)

    class Meta:
        model = Changeset
        fields = (
            'id', 'created', 'modified', 'closed', 'target_resource_type',
            'target_resource_id', 'user',
            'historical_browsers', 'historical_features',
            'historical_maturities', 'historical_sections',
            'historical_specifications', 'historical_supports',
            'historical_versions')
        update_only_fields = (
            'user', 'target_resource_type', 'target_resource_id')
        read_only_fields = (
            'id', 'created', 'modified',
            'historical_browsers', 'historical_features',
            'historical_maturities', 'historical_sections',
            'historical_specifications', 'historical_supports',
            'historical_versions')


class UserSerializer(ModelSerializer):
    """User Serializer"""

    created = DateField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'created')


#
# Historical object serializers
#
class HistoricalOptions(ModelSerializer._options_class):
    def __init__(self, meta):
        super(HistoricalOptions, self).__init__(meta)
        self.archive_link_fields = getattr(meta, 'archive_link_fields', [])
        self.archive_cached_links_fields = getattr(
            meta, 'archive_cached_links_fields', [])


class HistoricalObjectSerializer(ModelSerializer):
    """Common serializer attributes for Historical models"""
    _options_class = HistoricalOptions

    id = IntegerField(source="history_id")
    date = DateTimeField(source="history_date")
    event = SerializerMethodField('get_event')
    changeset = PrimaryKeyRelatedField(source="history_changeset")

    EVENT_CHOICES = {
        '+': 'created',
        '~': 'changed',
        '-': 'deleted',
    }

    def get_event(self, obj):
        return self.EVENT_CHOICES[obj.history_type]

    def get_archive(self, obj):
        serializer = self.ArchivedObject(obj)
        data = serializer.data
        data['id'] = str(data['id'])

        data['links'] = type(data)()  # Use dict-like type of serializer.data

        # Archived link fields are to-one relations
        for field in self.opts.archive_link_fields:
            del data[field]
            value = getattr(obj, field + '_id')
            if value is not None:
                value = str(value)
            data['links'][field] = value

        # Archived cached links fields are a list of primary keys
        for field in self.opts.archive_cached_links_fields:
            value = getattr(obj, field)
            value = [str(x) for x in value]
            data['links'][field] = value
        data['links']['history_current'] = str(obj.history_id)

        return data

    class Meta:
        fields = ('id', 'date', 'event', 'changeset')


class HistoricalBrowserSerializer(HistoricalObjectSerializer):

    class ArchivedObject(BrowserSerializer):
        class Meta(BrowserSerializer.Meta):
            exclude = ('history_current', 'history', 'versions')

    browser = HistoricalObjectField()
    browsers = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Browser.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'browser', 'browsers')


class HistoricalFeatureSerializer(HistoricalObjectSerializer):

    class ArchivedObject(FeatureSerializer):
        class Meta(FeatureSerializer.Meta):
            exclude = (
                'history_current', 'history', 'sections', 'supports',
                'children')

    feature = HistoricalObjectField()
    features = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Feature.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'feature', 'features')
        archive_link_fields = ('parent',)
        archive_cached_links_fields = ('sections',)


class HistoricalMaturitySerializer(HistoricalObjectSerializer):

    class ArchivedObject(MaturitySerializer):
        class Meta(MaturitySerializer.Meta):
            exclude = ('specifications', 'history_current', 'history')

    maturity = HistoricalObjectField()
    maturities = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Maturity.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'maturity', 'maturities')


class HistoricalSectionSerializer(HistoricalObjectSerializer):

    class ArchivedObject(SectionSerializer):
        class Meta(SectionSerializer.Meta):
            exclude = ('features', 'history_current', 'history')

    section = HistoricalObjectField()
    sections = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Section.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'section', 'sections')
        archive_link_fields = ('specification',)


class HistoricalSpecificationSerializer(HistoricalObjectSerializer):

    class ArchivedObject(SpecificationSerializer):
        class Meta(SpecificationSerializer.Meta):
            exclude = ('sections', 'history_current', 'history')

    specification = HistoricalObjectField()
    specifications = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Specification.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'specification', 'specifications')
        archive_link_fields = ('maturity',)


class HistoricalSupportSerializer(HistoricalObjectSerializer):

    class ArchivedObject(SupportSerializer):
        class Meta(SupportSerializer.Meta):
            exclude = ('history_current', 'history')

    support = HistoricalObjectField()
    supports = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Support.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'support', 'supports')
        archive_link_fields = ('version', 'feature')


class HistoricalVersionSerializer(HistoricalObjectSerializer):

    class ArchivedObject(VersionSerializer):
        class Meta(VersionSerializer.Meta):
            exclude = ('supports', 'history_current', 'history')

    version = HistoricalObjectField()
    versions = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Version.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'version', 'versions')
        archive_link_fields = ('browser',)


#
# View serializers
#

class ViewFeatureExtraSerializer(ModelSerializer):

    """Linked resources and metadata for ViewFeatureSerializer."""

    browsers = BrowserSerializer(source='all_browsers', many=True)
    features = FeatureSerializer(source='child_features', many=True)
    maturities = MaturitySerializer(source='all_maturities', many=True)
    sections = SectionSerializer(source='all_sections', many=True)
    specifications = SpecificationSerializer(source='all_specs', many=True)
    supports = SupportSerializer(source='all_supports', many=True)
    versions = VersionSerializer(source='all_versions', many=True)
    meta = SerializerMethodField('get_meta')

    def to_native(self, obj):
        """Add addditonal data for the ViewFeatureSerializer."""
        feature_pks = obj.get_descendants().values_list('pk', flat=True)
        obj.child_features = list(CachedQueryset(
            Cache(), Feature.objects.all(), feature_pks))

        section_pks = set(obj.sections.values_list('pk', flat=True))
        support_pks = set(obj.supports.values_list('pk', flat=True))
        for feature in obj.child_features:
            section_pks.update(feature.sections.values_list('id', flat=True))
            support_pks.update(feature.supports.values_list('id', flat=True))

        obj.all_sections = list(CachedQueryset(
            Cache(), Section.objects.all(), sorted(section_pks)))
        obj.all_supports = list(CachedQueryset(
            Cache(), Support.objects.all(), sorted(support_pks)))

        specification_pks = set()
        for section in obj.all_sections:
            specification_pks.add(section.specification.pk)
        obj.all_specs = list(CachedQueryset(
            Cache(), Specification.objects.all(), sorted(specification_pks)))

        maturity_pks = set()
        for specification in obj.all_specs:
            maturity_pks.add(specification.maturity.pk)
        obj.all_maturities = list(CachedQueryset(
            Cache(), Maturity.objects.all(), sorted(maturity_pks)))

        version_pks = set()
        for support in obj.all_supports:
            version_pks.add(support.version.pk)
        obj.all_versions = list(CachedQueryset(
            Cache(), Version.objects.all(), sorted(version_pks)))

        browser_pks = set()
        for version in obj.all_versions:
            browser_pks.add(version.browser.pk)
        obj.all_browsers = list(CachedQueryset(
            Cache(), Browser.objects.all(), sorted(browser_pks)))

        ret = super(ViewFeatureExtraSerializer, self).to_native(obj)
        return ret

    def significant_changes(self, obj):
        """Determine what versions are important for support changes.

        A version is important if it is the first version with support
        information, or it changes support from the previous version.
        """
        # Create lookup of ID/PK -> instances
        browsers = {}
        for browser in obj.all_browsers:
            # Cache version order
            browser.version_ids = browser.versions.values_list('id', flat=True)
            browsers[browser.id] = browser
        versions = dict(
            [(version.id, version) for version in obj.all_versions])
        features = dict(
            [(feature.id, feature) for feature in obj.child_features])
        features[obj.id] = obj

        # Create index of supported browser / version / features
        supported = []
        for support in obj.all_supports:
            version = versions[support.version.pk]
            browser = browsers[version.browser.pk]
            version_order = browser.version_ids.index(version.id)
            feature = features[support.feature.pk]
            supported.append((
                feature.id, browser.id, version_order, version.id,
                support.id, support.support))
        supported.sort()

        # Identify significant browser / version / supports by feature
        significant_changes = {}
        last_f_id = None
        last_b_id = None
        last_support = None
        for f_id, b_id, _, v_id, s_id, support in supported:
            if last_f_id != f_id:
                last_support = None
                last_f_id = f_id
            if last_b_id != b_id:
                last_support = None
                last_b_id = b_id

            if last_support != support:
                sig_feature = significant_changes.setdefault(str(f_id), {})
                sig_browser = sig_feature.setdefault(str(b_id), [])
                sig_browser.append(str(s_id))
                last_support = support
        return significant_changes

    def browser_tabs(self, obj):
        """Section and order the browser tabs.

        TODO: Move this logic into the database, API
        """
        known_browsers = dict((
            ('chrome', ('Desktop', 1)),
            ('firefox', ('Desktop', 2)),
            ('internet_explorer', ('Desktop', 3)),
            ('opera', ('Desktop', 4)),
            ('safari', ('Desktop', 5)),
            ('android', ('Mobile', 6)),
            ('chrome_for_android', ('Mobile', 7)),
            ('chrome_mobile', ('Mobile', 8)),
            ('firefox_mobile', ('Mobile', 9)),
            ('ie_mobile', ('Mobile', 10)),
            ('opera_mini', ('Mobile', 11)),
            ('opera_mobile', ('Mobile', 12)),
            ('safari_mobile', ('Mobile', 13)),
            ('blackberry', ('Mobile', 14)),
            ('firefox_os', ('Other', 15)),
        ))
        next_other = 16
        sections = ['Desktop', 'Mobile', 'Other']
        raw_tabs = dict((section, []) for section in sections)

        for browser in obj.all_browsers:
            try:
                section, order = known_browsers[browser.slug]
            except KeyError:
                section, order = ('Other', next_other)
                next_other += 1
            raw_tabs[section].append((order, browser.id))

        tabs = []
        for section in sections:
            browsers = raw_tabs[section]
            if browsers:
                browsers.sort()
                tabs.append(OrderedDict((
                    ('name', {'en': section}),
                    ('browsers', [str(pk) for _, pk in browsers]),
                )))
        return tabs

    def get_meta(self, obj):
        """Assemble the metadata for the feature view."""
        significant_changes = self.significant_changes(obj)
        browser_tabs = self.browser_tabs(obj)
        meta = OrderedDict((
            ('compat_table', OrderedDict((
                ('supports', significant_changes),
                ('tabs', browser_tabs),
            ))),))
        return meta

    class Meta:
        model = Feature
        fields = (
            'browsers', 'versions', 'supports', 'maturities',
            'specifications', 'sections', 'features', 'meta')


class ViewFeatureSerializer(FeatureSerializer):
    """Feature Serializer, plus related data and MDN browser compat logic"""

    _view_extra = ViewFeatureExtraSerializer(source='*')

    class Meta(FeatureSerializer.Meta):
        fields = FeatureSerializer.Meta.fields + ('_view_extra',)
