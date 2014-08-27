# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework.serializers import (
    DateField, DateTimeField, HyperlinkedRelatedField, IntegerField,
    ModelSerializer, ModelSerializerOptions, SerializerMethodField,
    ValidationError)


from .fields import (
    CurrentHistoryField, HistoricalObjectField,  HistoryField,
    LimitedPrimaryKeyRelatedField, SecureURLField, TranslatedTextField)
from .models import Browser, BrowserVersion


#
# "Regular" Serializers
#

class UpdateOnlySerializerOptions(ModelSerializerOptions):
    def __init__(self, meta):
        super(UpdateOnlySerializerOptions, self).__init__(meta)
        self.update_only_fields = getattr(meta, 'update_only_fields', ())


class UpdateOnlyMixin(object):
    _options_class = UpdateOnlySerializerOptions

    def get_fields(self):
        fields = super(UpdateOnlyMixin, self).get_fields()

        view = self.context.get('view', None)
        if view and view.action in ('list', 'create'):
            update_only_fields = getattr(self.opts, 'update_only_fields', [])
            for field_name in update_only_fields:
                fields[field_name].read_only = True

        return fields


class HistoricalModelSerializer(UpdateOnlyMixin, ModelSerializer):
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
            history_id = int(data['history_current'].split('/')[-1])
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

    icon = SecureURLField(required=False)
    name = TranslatedTextField()
    note = TranslatedTextField(required=False)
    browser_versions = LimitedPrimaryKeyRelatedField(many=True)

    def save_object(self, obj, **kwargs):
        if 'browser_versions' in getattr(obj, '_related_data', {}):
            versions = obj._related_data.pop('browser_versions')
        else:
            versions = None

        super(BrowserSerializer, self).save_object(obj, **kwargs)

        if versions:
            v_pks = [v.pk for v in versions]
            current_order = obj.get_browserversion_order()
            if v_pks != current_order:
                obj.set_browserversion_order(v_pks)

    class Meta:
        model = Browser
        fields = (
            'id', 'slug', 'icon', 'name', 'note', 'history',
            'history_current', 'browser_versions')
        update_only_fields = (
            'history', 'history_current', 'browser_versions')


class BrowserVersionSerializer(HistoricalModelSerializer):
    """Browser Version Serializer"""

    release_notes_uri = TranslatedTextField(required=False)
    note = TranslatedTextField(required=False)
    order = IntegerField(read_only=True, source='_order')

    class Meta:
        model = BrowserVersion
        fields = (
            'id', 'browser', 'version', 'release_day', 'retirement_day',
            'status', 'release_notes_uri', 'note', 'order', 'history',
            'history_current')


class UserSerializer(ModelSerializer):
    """User Serializer"""

    created = DateField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'created')


#
# Historical object serializers
#

class HistoricalObjectSerializer(ModelSerializer):
    '''Common serializer attributes for Historical models'''

    id = IntegerField(source="history_id")
    date = DateTimeField(source="history_date")
    event = SerializerMethodField('get_event')
    user = HyperlinkedRelatedField(
        source="history_user", view_name='user-detail')

    EVENT_CHOICES = {
        '+': 'created',
        '~': 'changed',
        '-': 'deleted',
    }

    def get_event(self, obj):
        return self.EVENT_CHOICES[obj.history_type]

    def get_archive(self, obj):
        serializer = self.ArchivedBrowser(obj)
        data = serializer.data
        data['id'] = str(data['id'])
        data['links'] = {'history_current': str(obj.history_id)}
        return data

    class Meta:
        fields = ('id', 'date', 'event', 'user')


class HistoricalBrowserSerializer(HistoricalObjectSerializer):

    class ArchivedBrowser(BrowserSerializer):
        class Meta(BrowserSerializer.Meta):
            exclude = ('history_current', 'history', 'browser_versions')

    browser = HistoricalObjectField(view_name='browser-detail')
    browsers = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = Browser.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'browser', 'browsers')


class HistoricalBrowserVersionSerializer(HistoricalObjectSerializer):

    class ArchivedBrowser(BrowserVersionSerializer):
        class Meta(BrowserVersionSerializer.Meta):
            exclude = ('history_current', 'history', 'browser')

    browser_version = HistoricalObjectField(view_name='browserversion-detail')
    browser_versions = SerializerMethodField('get_archive')

    class Meta(HistoricalObjectSerializer.Meta):
        model = BrowserVersion.history.model
        fields = HistoricalObjectSerializer.Meta.fields + (
            'browser_version', 'browser_versions')
