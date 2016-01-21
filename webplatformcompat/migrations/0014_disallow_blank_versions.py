# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0013_convert_empty_versions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalversion',
            name='version',
            field=models.CharField(help_text='Version string.', max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='version',
            name='version',
            field=models.CharField(help_text='Version string.', max_length=20),
            preserve_default=True,
        ),
    ]
