# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework.serializers import DateField, ModelSerializer

from .fields import TranslatedTextField, URLOrNullField
from .models import Browser


class UserSerializer(ModelSerializer):
    """User Serializer"""

    created = DateField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'created')


class BrowserSerializer(ModelSerializer):
    """Browser Serializer"""

    icon = URLOrNullField(required=False)
    name = TranslatedTextField()
    note = TranslatedTextField(required=False)

    class Meta:
        model = Browser
        fields = ('id', 'slug', 'icon', 'name', 'note')
