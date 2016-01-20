# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0005_data_add_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeset',
            name='user',
            field=models.ForeignKey(
                related_name='changesets', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
