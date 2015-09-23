# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0008_switch_modified_to_datetimefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featurepage',
            name='feature',
            field=models.OneToOneField(to='webplatformcompat.Feature', help_text='Feature in API'),
        ),
    ]
