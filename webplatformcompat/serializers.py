# -*- coding: utf-8 -*-
"""
API Serializers
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""

    created = serializers.DateField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'created')
