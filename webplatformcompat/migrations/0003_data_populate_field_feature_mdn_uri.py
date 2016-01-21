# -*- coding: utf-8 -*-
"""Populate the Feature.new_mdn_path field from Feature.mdn_path."""
from __future__ import unicode_literals
import json

from django.db import migrations


def set_uri_from_path(features):
    for feature in features:
        if feature.mdn_path:
            feature.mdn_uri = json.dumps(
                {'en': 'https://developer.mozilla.org/' + feature.mdn_path})
        else:
            feature.mdn_uri = None
        feature._delay_cache = True
        feature.save()


def populate_feature_mdn_uri(apps, schema_editor):
    Feature = apps.get_model('webplatformcompat', 'Feature')
    set_uri_from_path(Feature.objects.all())

    HistoricalFeature = apps.get_model(
        'webplatformcompat', 'HistoricalFeature')
    set_uri_from_path(HistoricalFeature.objects.all())


def set_path_from_uri(features):
    for feature in features:
        if feature.mdn_uri:
            en_uri = feature.mdn_uri.get('en', None)
            feature.mdn_path = en_uri
        else:
            feature.mdn_path = None
        feature._delay_cache = True
        feature.save()


def flush_feature_mdn_uri(apps, schema_editor):
    Feature = apps.get_model('webplatformcompat', 'Feature')
    set_path_from_uri(Feature.objects.all())
    HistoricalFeature = apps.get_model(
        'webplatformcompat', 'HistoricalFeature')
    set_path_from_uri(HistoricalFeature.objects.all())


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0002_add_field_feature_mdn_uri'),
    ]

    operations = [
        migrations.RunPython(
            populate_feature_mdn_uri, flush_feature_mdn_uri)
    ]
