# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0006_update_issue_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featurepage',
            name='status',
            field=models.IntegerField(default=0, help_text='Status of MDN Parsing process', choices=[(0, 'Starting Import'), (1, 'Fetching Metadata'), (2, 'Fetching MDN pages'), (3, 'Parsing MDN pages'), (4, 'Parsing Complete'), (5, 'Scraping Failed'), (6, 'No Compat Data'), (7, 'Has Warnings'), (8, 'Has Errors'), (9, 'Has Critical Errors')]),
            preserve_default=True,
        ),
    ]
