# -*- coding: utf-8 -*-
"""Extentions for simplehistory"""

from __future__ import unicode_literals

from django.utils.timezone import now

from simple_history.models import HistoricalRecords as BaseHistoricalRecords


def register(
        model, app=None, manager_name='history', records_class=None,
        **records_config):
    """
    Create historical model for `model` and attach history manager to `model`.

    Variant of simple_history.register that allows override of records class
    """
    from simple_history import models
    if model._meta.db_table not in models.registered_models:
        records_class = records_class or HistoricalRecords
        records = records_class(**records_config)
        records.manager_name = manager_name
        records.module = app and ("%s.models" % app) or model.__module__
        records.add_extra_methods(model)
        records.finalize(model)
        models.registered_models[model._meta.db_table] = model
    else:
        pass  # pragma: nocover


class HistoricalRecords(BaseHistoricalRecords):
    """simplehistory.HistoricalRecords with modifications

    Can easily add additional fields
    """
    additional_fields = {}

    def copy_fields(self, model):
        """Add additional_fields to the historic model"""
        fields = super(HistoricalRecords, self).copy_fields(model)
        for name, field in self.additional_fields.items():
            assert name not in fields
            assert hasattr(self, 'get_%s_value' % name)
            fields[name] = field
        return fields

    def create_historical_record(self, instance, type):
        """Add extra data when creating the historic record"""
        history_date = getattr(instance, '_history_date', now())
        history_user = self.get_history_user(instance)
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)

        # New code - add additional data
        for field_name in self.additional_fields:
            loader = getattr(self, 'get_%s_value' % field_name)
            value = loader(instance, type)
            attrs[field_name] = value

        manager.create(history_date=history_date, history_type=type,
                       history_user=history_user, **attrs)
