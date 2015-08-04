# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django_extensions.db.fields.json
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0009_drop_support_footnote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalfeature',
            name='parent_id',
        ),
        migrations.RemoveField(
            model_name='historicalsection',
            name='specification_id',
        ),
        migrations.RemoveField(
            model_name='historicalspecification',
            name='maturity_id',
        ),
        migrations.RemoveField(
            model_name='historicalsupport',
            name='feature_id',
        ),
        migrations.RemoveField(
            model_name='historicalsupport',
            name='version_id',
        ),
        migrations.RemoveField(
            model_name='historicalversion',
            name='browser_id',
        ),
        migrations.AddField(
            model_name='historicalfeature',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Feature'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalsection',
            name='specification',
            field=models.ForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Specification'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalspecification',
            name='maturity',
            field=models.ForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Maturity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalsupport',
            name='feature',
            field=models.ForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Feature'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalsupport',
            name='version',
            field=models.ForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalversion',
            name='browser',
            field=models.ForeignKey(blank=True, null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='webplatformcompat.Browser'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalbrowser',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalfeature',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalfeature',
            name='sections',
            field=django_extensions.db.fields.json.JSONField(default='[]'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalmaturity',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalsection',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalspecification',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalsupport',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='historicalversion',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
