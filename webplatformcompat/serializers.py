# -*- coding: utf-8 -*-
"""API Serializers"""
from collections import OrderedDict

from django.db.models import CharField
from django.contrib.auth.models import User
from rest_framework.serializers import (
    CurrentUserDefault, DateTimeField, IntegerField,
    ModelSerializer, SerializerMethodField, ValidationError)
from sortedm2m.fields import SortedManyToManyField

from . import fields
from .drf_fields import (
    CurrentHistoryField, HistoricalObjectField, HistoryField,
    MPTTRelationField, OptionalCharField, OptionalIntegerField,
    PrimaryKeyRelatedField, TranslatedTextField)
from .history import Changeset
from .models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)
from .validators import VersionAndStatusValidator


def omit_some(source_list, *omitted):
    """Return a list with some items omitted"""
    for item in omitted:
        assert item in source_list, '%r not in %r' % (item, source_list)
    return [x for x in source_list if x not in omitted]


#
# "Regular" Serializers
#
class WriteRestrictedMixin(object):

    def get_fields(self):
        """Add read_only flag for write-restricted fields"""
        fields = super(WriteRestrictedMixin, self).get_fields()

        # Some fields are read-only based on view action
        view = self.context.get('view', None)
        if view and view.action in ('list', 'create'):
            set_to_readonly = 'update_only'
        elif view and view.action in ('update', 'partial_update'):
            set_to_readonly = 'create_only'
        else:
            set_to_readonly = None

        # Set fields to read-only based on view action
        if set_to_readonly:
            fields_extra = getattr(self.Meta, 'fields_extra', {})
            for field_name, field in fields.items():
                field_extra = fields_extra.get(field_name, {})
                writable = field_extra.get('writable', True)
                if writable == set_to_readonly:
                    assert not field.read_only
                    field.read_only = True

        return fields


class FieldMapMixin(object):
    """Automatically handle fields used by this project"""
    serializer_field_mapping = ModelSerializer.serializer_field_mapping
    serializer_field_mapping[fields.TranslatedField] = TranslatedTextField
    serializer_field_mapping[CharField] = OptionalCharField
    serializer_field_mapping[SortedManyToManyField] = PrimaryKeyRelatedField
    serializer_related_field = PrimaryKeyRelatedField

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super(
            FieldMapMixin, self).build_standard_field(
                field_name, model_field)
        if isinstance(model_field, fields.TranslatedField):
            if not (model_field.blank or model_field.null):
                field_kwargs['required'] = True
            if model_field.allow_canonical:
                field_kwargs['allow_canonical'] = True
        return field_class, field_kwargs


class HistoricalModelSerializer(
        WriteRestrictedMixin, FieldMapMixin, ModelSerializer):
    """Model serializer with history manager"""
    omit_historical_fields = (
        'id', 'history_id', 'history_date', 'history_user', 'history_type',
        'history_changeset')

    def build_property_field(self, field_name, model_class):
        """Handle history field.

        The history field is a list of PKs for all the history records.
        """
        assert field_name == 'history'
        field_kwargs = {'many': True, 'read_only': True}
        return HistoryField, field_kwargs

    def build_unknown_field(self, field_name, model_class):
        """Handle history_current field.

        history_current returns the PK of the most recent history record.
        It is treated as read-only unless it is an update view.
        """
        assert field_name == 'history_current'
        return CurrentHistoryField, {}

    def to_internal_value(self, data):
        """If history_current in data, load historical data into instance"""
        if data and 'history_current' in data:
            history_id = int(data['history_current'])
            current_history = self.instance.history.all()[0]
            if current_history.history_id != history_id:
                try:
                    historical = self.instance.history.get(
                        history_id=history_id)
                except self.instance.history.model.DoesNotExist:
                    err = 'Invalid history ID for this object'
                    raise ValidationError({'history_current': [err]})
                else:
                    for field in historical._meta.fields:
                        if field.attname in self.omit_historical_fields:
                            continue
                        attname = field.attname
                        hist_value = getattr(historical, attname)
                        data_name = attname
                        if data_name.endswith('_id'):
                            data_name = data_name[:-len('_id')]
                        data[data_name] = hist_value
        return super(HistoricalModelSerializer, self).to_internal_value(data)


class BrowserSerializer(HistoricalModelSerializer):
    """Browser Serializer"""

    def update(self, instance, validated_data):
        versions = validated_data.pop('versions', None)
        instance = super(BrowserSerializer, self).update(
            instance, validated_data)

        if versions:
            v_pks = [v.pk for v in versions]
            current_order = instance.get_version_order()
            if v_pks != current_order:
                instance.set_version_order(v_pks)
        return instance

    class Meta:
        model = Browser
        fields = (
            'id', 'slug', 'name', 'note', 'history', 'history_current',
            'versions')
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'slug': {
                'writable': 'create_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'versions': {
                'link': 'from_many',
                'writable': 'update_only',
            },
        }


class FeatureSerializer(HistoricalModelSerializer):
    """Feature Serializer"""

    children = MPTTRelationField(
        many=True, queryset=Feature.objects.all(), required=False)

    def update(self, instance, validated_data):
        children = validated_data.pop('children', None)
        if children:
            current_order = list(instance.get_children())
            if current_order == children:
                children = None
        instance = super(FeatureSerializer, self).update(
            instance, validated_data)

        if children:
            instance.set_children_order(children)
        return instance

    def validate_children(self, value):
        if self.instance:
            current_children = list(self.instance.get_children())
            current_set = set([child.pk for child in current_children])
            new_set = set([child.pk for child in value])
            if current_set - new_set:
                raise ValidationError(
                    "All child features must be included in children.")
            if new_set - current_set:
                raise ValidationError(
                    "Set child.parent to add a child feature.")
        else:
            if value != []:  # pragma: no cover
                # Because children is in update_only_fields, never happens
                raise ValidationError(
                    "Can not set children when creating a feature.")
        return value

    class Meta:
        model = Feature
        fields = (
            'id', 'slug', 'mdn_uri', 'experimental', 'standardized',
            'stable', 'obsolete', 'name',
            'sections', 'supports', 'parent', 'children',
            'history_current', 'history')
        read_only_fields = ('supports',)
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'sections': {
                'link': 'from_many',
            },
            'supports': {
                'archive': 'omit',
                'link': 'from_many',
            },
            'parent': {
                'link': 'to_one',
            },
            'children': {
                'link': 'from_many',
                'writable': 'update_only'
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


class MaturitySerializer(HistoricalModelSerializer):
    """Specification Maturity Serializer"""

    class Meta:
        model = Maturity
        fields = (
            'id', 'slug', 'name', 'specifications',
            'history_current', 'history')
        read_only_fields = ('specifications',)
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'specifications': {
                'archive': 'omit',
                'link': 'from_many',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


class SectionSerializer(HistoricalModelSerializer):
    """Specification Section Serializer"""

    class Meta:
        model = Section
        fields = (
            'id', 'number', 'name', 'subpath', 'note', 'specification',
            'features', 'history_current', 'history')
        extra_kwargs = {
            'features': {
                'default': []
            }
        }
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'specification': {
                'link': 'to_one',
            },
            'features': {
                'archive': 'omit',
                'link': 'from_many',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


class SpecificationSerializer(HistoricalModelSerializer):
    """Specification Serializer"""

    def update(self, instance, validated_data):
        sections = validated_data.pop('sections', None)
        instance = super(SpecificationSerializer, self).update(
            instance, validated_data)

        if sections:
            s_pks = [s.pk for s in sections]
            current_order = instance.get_section_order()
            if s_pks != current_order:
                instance.set_section_order(s_pks)

        return instance

    class Meta:
        model = Specification
        fields = (
            'id', 'slug', 'mdn_key', 'name', 'uri', 'maturity', 'sections',
            'history_current', 'history')
        extra_kwargs = {
            'sections': {
                'default': []
            }
        }
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'maturity': {
                'link': 'to_one',
            },
            'sections': {
                'link': 'from_many',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


class SupportSerializer(HistoricalModelSerializer):
    """Support Serializer"""

    class Meta:
        model = Support
        fields = (
            'id', 'version', 'feature', 'support', 'prefix',
            'prefix_mandatory', 'alternate_name', 'alternate_mandatory',
            'requires_config', 'default_config', 'protected', 'note',
            'history_current', 'history')
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'version': {
                'link': 'to_one',
            },
            'feature': {
                'link': 'to_one',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


class VersionSerializer(HistoricalModelSerializer):
    """Browser Version Serializer"""

    order = IntegerField(read_only=True, source='_order')

    class Meta:
        model = Version
        fields = (
            'id', 'browser', 'version', 'release_day', 'retirement_day',
            'status', 'release_notes_uri', 'note', 'order',
            'supports', 'history', 'history_current')
        extra_kwargs = {
            'version': {
                'allow_blank': False
            }
        }
        read_only_fields = ('supports',)
        validators = [VersionAndStatusValidator()]
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'browser': {
                'link': 'to_one',
            },
            'version': {
                'writable': 'create_only',
            },
            'supports': {
                'archive': 'omit',
                'link': 'from_many',
            },
            'history_current': {
                'archive': 'history_id',
                'link': 'from_one',
                'writable': 'update_only',
            },
            'history': {
                'archive': 'omit',
                'link': 'from_many',
            },
        }


#
# Change control object serializers
#

class ChangesetSerializer(ModelSerializer):
    """Changeset Serializer"""

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
        read_only_fields = (
            'id', 'created', 'modified',
            'historical_browsers', 'historical_features',
            'historical_maturities', 'historical_sections',
            'historical_specifications', 'historical_supports',
            'historical_versions')
        extra_kwargs = {
            'user': {
                'default': CurrentUserDefault()
            }
        }
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'user': {
                'link': 'to_one',
                'writable': 'update_only',
            },
            'target_resource_type': {
                'writable': 'update_only',
            },
            'target_resource_id': {
                'writable': 'update_only',
            },
            'historical_browsers': {
                'link': 'from_many',
            },
            'historical_features': {
                'link': 'from_many',
            },
            'historical_maturities': {
                'link': 'from_many',
            },
            'historical_specifications': {
                'link': 'from_many',
            },
            'historical_sections': {
                'link': 'from_many',
            },
            'historical_supports': {
                'link': 'from_many',
            },
            'historical_versions': {
                'link': 'from_many',
            },
        }


class UserSerializer(ModelSerializer):
    """User Serializer"""

    created = DateTimeField(source='date_joined', read_only=True)
    agreement = SerializerMethodField()
    permissions = SerializerMethodField()

    def get_agreement(self, obj):
        """What version of the contribution terms did the user agree to?

        Placeholder for when we have a license agreement.
        """
        return 0

    def get_permissions(self, obj):
        """Return names of django.contrib.auth Groups

        Can not be used with a writable view, since django.contrib.auth User
        doesn't have this method.  Will need updating or a proxy class.
        """
        assert hasattr(obj, 'group_names'), "Expecting cached User object"
        return obj.group_names

    class Meta:
        model = User
        fields = (
            'id', 'username', 'created', 'agreement', 'permissions',
            'changesets')
        read_only_fields = ('username', 'changesets')
        fields_extra = {
            'id': {
                'link': 'self',
            },
            'changesets': {
                'link': 'from_many',
            },
        }


#
# Historical object serializers
#


class ArchiveMixin(object):
    def get_fields(self):
        """Modify fields when loading or preparing an archive."""
        fields = super(ArchiveMixin, self).get_fields()
        fields_extra = getattr(self.Meta, 'fields_extra', {})
        for field_name, field in fields.items():
            field_extra = fields_extra.get(field_name, {})
            archive = field_extra.get('archive')
            link = field_extra.get('link')
            if archive == 'omit':
                # Does not appear in archived representation
                del fields[field_name]
            elif link in ('from_one', 'from_many'):
                # Defer loading until HistoricalObjectSerializer.get_archive
                del fields[field_name]
            elif link == 'to_one':
                # Use the name_id field
                field.source = field_name + '_id'
        return fields


class HistoricalObjectSerializer(ModelSerializer):
    """Common serializer attributes for Historical models"""

    id = IntegerField(source="history_id")
    date = DateTimeField(source="history_date")
    event = SerializerMethodField()
    changeset = PrimaryKeyRelatedField(
        source="history_changeset", read_only=True)

    EVENT_CHOICES = {
        '+': 'created',
        '~': 'changed',
        '-': 'deleted',
    }

    def get_event(self, obj):
        return self.EVENT_CHOICES[obj.history_type]

    def get_archive(self, obj):
        serializer = self.ArchivedObject(obj)
        raw_data = serializer.data
        data = OrderedDict()
        links = OrderedDict()
        fields = serializer.Meta.fields
        fields_extra = getattr(serializer.Meta, 'fields_extra', {})
        for name in fields:
            field_extra = fields_extra.get(name, {})
            archive = field_extra.get('archive', 'include')
            if archive == 'include':
                link = field_extra.get('link')
                if link is None:
                    # Archived attribute
                    data[name] = raw_data[name]
                elif link == 'self':
                    # Archived self-id
                    data['id'] = str(raw_data[name])
                elif link == 'to_one':
                    value = getattr(obj, name + '_id')
                    if value is not None:
                        value = str(value)
                    links[name] = value
                else:
                    assert link == 'from_many', 'Unhandled link "%s"' % link
                    related = getattr(obj, name)
                    links[name] = [str(rel.pk) for rel in related]
            elif archive == 'history_id':
                links[name] = str(obj.history_id)
            else:
                assert archive == 'omit'
        data['links'] = links
        return data

    class Meta:
        fields = ('id', 'date', 'event', 'changeset')


class HistoricalBrowserSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, BrowserSerializer):
        class Meta(BrowserSerializer.Meta):
            fields = (
                'id', 'slug', 'name', 'note', 'versions', 'history',
                'history_current')

    browser = HistoricalObjectField()
    browsers = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Browser.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'browser', 'browsers')


class HistoricalFeatureSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, FeatureSerializer):
        class Meta(FeatureSerializer.Meta):
            fields = (
                'id', 'slug', 'mdn_uri', 'experimental', 'standardized',
                'stable', 'obsolete', 'name',
                'supports', 'parent', 'children', 'sections',
                'history_current', 'history')

    feature = HistoricalObjectField()
    features = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Feature.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'feature', 'features')


class HistoricalMaturitySerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, MaturitySerializer):
        class Meta(MaturitySerializer.Meta):
            pass

    maturity = HistoricalObjectField()
    maturities = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Maturity.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'maturity', 'maturities')


class HistoricalSectionSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, SectionSerializer):
        pass

    section = HistoricalObjectField()
    sections = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Section.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'section', 'sections')


class HistoricalSpecificationSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, SpecificationSerializer):
        pass

    specification = HistoricalObjectField()
    specifications = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Specification.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'specification', 'specifications')


class HistoricalSupportSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, SupportSerializer):
        pass

    support = HistoricalObjectField()
    supports = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Support.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'support', 'supports')


class HistoricalVersionSerializer(HistoricalObjectSerializer):

    class ArchivedObject(ArchiveMixin, VersionSerializer):
        pass

    version = HistoricalObjectField()
    versions = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Version.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'version', 'versions')
