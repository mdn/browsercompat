# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.forms import Textarea
from rest_framework.fields import CharField, URLField

from .validators import LanguageDictValidator, SecureURLValidator


class TranslatedTextField(CharField):
    """Field is a dictionary of language codes to text"""
    def __init__(self, *args, **kwargs):
        widget = kwargs.pop('widget', Textarea)
        validators = kwargs.pop('validators', [LanguageDictValidator()])
        super(TranslatedTextField, self).__init__(
            widget=widget, validators=validators, *args, **kwargs)

    def to_native(self, value):
        if value:
            return value
        else:
            return None

    def from_native(self, value):
        if isinstance(value, dict):
            return value
        value = value.strip()
        if value:
            try:
                return json.loads(value)
            except ValueError as e:
                raise ValidationError(str(e))
        else:
            return None


class EmptyIsNullMixin(object):
    """Convert empty values to null"""
    def to_native(self, value):
        return super(EmptyIsNullMixin, self).to_native(value) or None


class SecureURLField(EmptyIsNullMixin, URLField):
    def __init__(self, *args, **kwargs):
        validators = kwargs.pop('validators', [SecureURLValidator()])
        super(SecureURLField, self).__init__(
            validators=validators, *args, **kwargs)
