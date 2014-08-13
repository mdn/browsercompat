# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.forms import Textarea
from rest_framework.fields import CharField, URLField


class TranslatedTextField(CharField):
    """Field is a dictionary of language codes to text"""
    def __init__(self, *args, **kwargs):
        widget = kwargs.pop('widget', Textarea)
        super(TranslatedTextField, self).__init__(
            widget=widget, *args, **kwargs)

    def to_native(self, value):
        if value:
            return value
        else:
            return None

    def from_native(self, value):
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


class URLOrNullField(EmptyIsNullMixin, URLField):
    pass
