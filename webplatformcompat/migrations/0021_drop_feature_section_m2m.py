# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0020_populate_references'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feature',
            name='sections',
        ),
        migrations.RemoveField(
            model_name='historicalfeature',
            name='sections',
        ),
        migrations.RemoveField(
            model_name='historicalsection',
            name='note',
        ),
        migrations.RemoveField(
            model_name='section',
            name='note',
        ),
        migrations.AlterField(
            model_name='historicalfeature',
            name='references',
            field=django_extensions.db.fields.json.JSONField(default='[]'),
        ),
    ]
