# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0016_feature_sections_allow_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalbrowser',
            name='versions',
            field=django_extensions.db.fields.json.JSONField(default='[]'),
        ),
        migrations.AddField(
            model_name='historicalfeature',
            name='children',
            field=django_extensions.db.fields.json.JSONField(default='[]'),
        ),
        migrations.AddField(
            model_name='historicalspecification',
            name='sections',
            field=django_extensions.db.fields.json.JSONField(default='[]'),
        ),
    ]
