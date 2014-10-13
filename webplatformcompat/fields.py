# -*- coding: utf-8 -*-
"""
Fields for Django models
"""
from django.db.models import URLField
from django_extensions.db.fields.json import JSONField

from .validators import LanguageDictValidator, SecureURLValidator


class TranslatedField(JSONField):
    '''A JSONField that holds translated strings'''

    def __init__(self, *args, **kwargs):
        self.allow_canonical = kwargs.pop('allow_canonical', False)
        validators = kwargs.pop(
            'validators', [LanguageDictValidator(self.allow_canonical)])
        super(TranslatedField, self).__init__(
            validators=validators, *args, **kwargs)


class SecureURLField(URLField):
    '''An URLField that requires protocol https://'''

    def __init__(self, *args, **kwargs):
        validators = kwargs.pop('validators', [SecureURLValidator()])
        super(SecureURLField, self).__init__(
            validators=validators, *args, **kwargs)
