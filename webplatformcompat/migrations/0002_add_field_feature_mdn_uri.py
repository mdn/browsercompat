# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
import webplatformcompat.validators
import webplatformcompat.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='mdn_uri',
            field=webplatformcompat.fields.TranslatedField(help_text='The URI of the MDN page that documents this feature.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalfeature',
            name='mdn_uri',
            field=webplatformcompat.fields.TranslatedField(help_text='The URI of the MDN page that documents this feature.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
            preserve_default=True,
        ),
    ]
