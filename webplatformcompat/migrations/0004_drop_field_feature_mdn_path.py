# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0003_data_populate_field_feature_mdn_uri'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feature',
            name='mdn_path',
        ),
        migrations.RemoveField(
            model_name='historicalfeature',
            name='mdn_path',
        ),
    ]
