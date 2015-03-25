# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
import webplatformcompat.validators
import webplatformcompat.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0008_move_support_footnotes_to_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsupport',
            name='footnote',
        ),
        migrations.RemoveField(
            model_name='support',
            name='footnote',
        ),
        migrations.AlterField(
            model_name='historicalsupport',
            name='note',
            field=webplatformcompat.fields.TranslatedField(help_text='Notes for this support', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='support',
            name='note',
            field=webplatformcompat.fields.TranslatedField(help_text='Notes for this support', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
            preserve_default=True,
        ),
    ]
