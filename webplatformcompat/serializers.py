# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework.serializers import DateField, ModelSerializer

from .fields import (
    TranslatedTextField, SecureURLField, HistoryField, CurrentHistoryField)
from .models import Browser, BrowserVersion


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


class UserSerializer(ModelSerializer):
    """User Serializer"""

    created = DateField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'created')


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
