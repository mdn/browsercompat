# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.forms import Textarea
from rest_framework.serializers import (
    CharField, HyperlinkedRelatedField, URLField)

from .validators import LanguageDictValidator, SecureURLValidator


class HistoryField(HyperlinkedRelatedField):
    """Field is the history manager

    To use this field, initialize 'source' to the name of the
    HistoricalRecords object (defaults to 'history')
    """

    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        assert many, 'many must be True'
        read_only = kwargs.pop('read_only', True)
        assert read_only, 'read_only must be True'
        super(HistoryField, self).__init__(
            many=many, read_only=read_only, *args, **kwargs)

    def initialize(self, parent, field_name):
        """Initialize field

        history only makes sense in the context of an object.  However, some
        views, such as the browsable API, might try to access the queryset
        outside of an object context.  We initialize the queryset to the none()
        queryset, so certain operations (such as determining the model or
        calling all()) will return expected data.
        """
        manager = getattr(parent.opts.model, self.source or field_name)
        self.full_queryset = manager
        self.queryset = manager.none()
        super(HistoryField, self).initialize(parent, field_name)

    def field_to_native(self, obj, field_name):
        """Convert to list of history PKs

        With a valid object, the queryset can be set to the proper history for
        this object.  In some views, such as the browsable API for the list,
        the object is not set, so we leave it as the none() queryset set in
        initialize.
        """
        self.queryset = getattr(obj, self.source or field_name)
        return super(HistoryField, self).field_to_native(obj, field_name)

    def get_object(self, queryset, view_name, args, kwargs):
        """Get the specified object

        When getting a list of items, the field_to_native call might limit
        self.queryset to its own instance.  This falls back to the full
        queryset of historical objects.
        """
        assert queryset == self.queryset
        return super(HistoryField, self).get_object(
            self.full_queryset, view_name, args, kwargs)


class CurrentHistoryField(HyperlinkedRelatedField):
    """Field is the current history object

    To use this field, initialize the manager to the name of the
    HistoricalRecords object (defaults to 'history')
    """

    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', 'history')
        required = kwargs.pop('required', False)
        assert not required, 'required must be False'
        read_only = kwargs.pop('read_only', True)
        assert read_only, 'read_only must be True (for now)'
        super(CurrentHistoryField, self).__init__(
            required=required, read_only=read_only, *args, **kwargs)

    def initialize(self, parent, field_name):
        """Initialize field

        history_current only makes sense in the context of an object.
        However, some views, such as the browsable API, might try to access
        the queryset outside of an object context.  We initialize the
        queryset to the none() queryset, so certain operations (such as
        determining the model or calling all()) will return expected data.
        """
        self.full_queryset = getattr(parent.opts.model, self.manager)
        self.queryset = self.full_queryset.none()
        super(CurrentHistoryField, self).initialize(parent, field_name)

    def field_to_native(self, obj, field_name):
        """Convert to the ID of the current history

        With a valid object, the queryset can be set to the proper history for
        this object.  In some views, such as the browsable API for the list,
        the object is not set, so we leave it as the none() queryset set in
        initialize.
        """
        self.queryset = getattr(obj, self.manager)
        most_recent = self.queryset.most_recent()
        return self.to_native(most_recent)

    def get_object(self, queryset, view_name, args, kwargs):
        """Get the specified object

        When getting a list of items, the field_to_native call might limit
        self.queryset to its own instance.  This falls back to the full
        queryset of historical objects.
        """
        assert queryset == self.queryset
        return super(CurrentHistoryField, self).get_object(
            self.full_queryset, view_name, args, kwargs)


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
