# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0010_data_remove_non_english_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='featurepage',
            name='committed',
            field=models.IntegerField(default=0, help_text='Is the data committed to the API?', db_index=True, choices=[(0, 'Unknown'), (1, 'Not Committed'), (2, 'Committed'), (3, 'New Data'), (4, 'Blocking Issues'), (5, 'No Data')]),
        ),
        migrations.AddField(
            model_name='featurepage',
            name='converted_compat',
            field=models.IntegerField(default=0, help_text='Does the MDN page include {{EmbedCompatTable}}?', db_index=True, choices=[(0, 'Unknown'), (1, 'Not Converted'), (2, 'Converted'), (3, 'Slug Mismatch'), (4, 'No Data')]),
        ),
        migrations.AlterField(
            model_name='featurepage',
            name='modified',
            field=models.DateTimeField(help_text='Last modification time', auto_now=True),
        ),
        migrations.AlterField(
            model_name='featurepage',
            name='status',
            field=models.IntegerField(default=0, help_text='Status of MDN Parsing process', db_index=True, choices=[(0, 'Starting Import'), (1, 'Fetching Metadata'), (2, 'Fetching MDN pages'), (3, 'Parsing MDN pages'), (4, 'Parsing Complete'), (5, 'Scraping Failed'), (6, 'No Compat Data'), (7, 'Has Warnings'), (8, 'Has Errors'), (9, 'Has Critical Errors')]),
        ),
    ]
