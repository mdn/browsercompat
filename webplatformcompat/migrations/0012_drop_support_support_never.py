# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0011_convert_support_never'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsupport',
            name='support',
            field=models.CharField(choices=[('yes', 'yes'), ('no', 'no'), ('partial', 'partial'), ('unknown', 'unknown')], help_text='Does the browser version support this feature?', max_length=10, default='yes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='support',
            name='support',
            field=models.CharField(choices=[('yes', 'yes'), ('no', 'no'), ('partial', 'partial'), ('unknown', 'unknown')], help_text='Does the browser version support this feature?', max_length=10, default='yes'),
            preserve_default=True,
        ),
    ]
