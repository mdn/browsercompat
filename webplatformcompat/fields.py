# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.fields import CharField


class EmptyIsNullMixin(object):
    """Convert empty values to null"""
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        super(EmptyIsNullMixin, self).__init__(
            self, required=required, *args, **kwargs)

    def to_native(self, value):
        return super(EmptyIsNullMixin, self).to_native(value) or None


class CharOrNullField(EmptyIsNullMixin, CharField):
    pass
