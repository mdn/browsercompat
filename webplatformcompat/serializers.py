# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework.serializers import DateField, ModelSerializer

from .fields import (
    TranslatedTextField, SecureURLField, HistoryField, CurrentHistoryField)
from .models import Browser


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

        name = 'history'
        assert name in self.opts.fields and name not in fields
        fields[name] = HistoryField(view_name=view_name)

        name = 'history_current'
        assert name in self.opts.fields and name not in fields
        fields[name] = CurrentHistoryField(view_name=view_name)

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
            'history_current')
