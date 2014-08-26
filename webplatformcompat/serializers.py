# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework.serializers import (
    DateField, DateTimeField, HyperlinkedRelatedField, IntegerField,
    ModelSerializer, SerializerMethodField)

from .fields import (
    CurrentHistoryField, HistoricalObjectField,  HistoryField, SecureURLField,
    TranslatedTextField)
from .models import Browser, BrowserVersion


#
# "Regular" Serializers
#


class HistoricalModelSerializer(ModelSerializer):
    """Model serializer with history manager"""

    def __init__(self, *args, **kwargs):
        """Add history and history_current fields"""
        return super(HistoricalModelSerializer, self).__init__(
            *args, **kwargs)

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
        fields['history_current'] = CurrentHistoryField(view_name=view_name)

        return fields


class BrowserSerializer(HistoricalModelSerializer):
    """Browser Serializer"""

    icon = SecureURLField(required=False)
    name = TranslatedTextField()
    note = TranslatedTextField(required=False)

    class Meta:
        model = Browser
        fields = (
            'id', 'slug', 'icon', 'name', 'note', 'history',
            'history_current', 'browser_versions')


class BrowserVersionSerializer(HistoricalModelSerializer):
    """Browser Version Serializer"""

    release_notes_uri = TranslatedTextField(required=False)
    note = TranslatedTextField(required=False)

    class Meta:
        model = BrowserVersion
        fields = (
            'id', 'browser', 'version', 'release_day', 'retirement_day',
            'status', 'release_notes_uri', 'note', 'history',
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
