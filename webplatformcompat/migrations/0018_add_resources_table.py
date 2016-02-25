# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
import webplatformcompat.validators
import webplatformcompat.fields
import webplatformcompat.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webplatformcompat', '0017_add_historical_orders'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalReference',
            fields=[
                ('id', models.IntegerField(blank=True, verbose_name='ID', db_index=True, auto_created=True)),
                ('note', webplatformcompat.fields.TranslatedField(blank=True, help_text='Notes for this section', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('_order', models.IntegerField(editable=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, null=True, blank=True, to='webplatformcompat.Feature', related_name='+', db_constraint=False)),
                ('history_changeset', models.ForeignKey(to='webplatformcompat.Changeset', related_name='historical_references')),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, null=True, blank=True, to='webplatformcompat.Section', related_name='+', db_constraint=False)),
            ],
            options={
                'verbose_name': 'historical reference',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', webplatformcompat.fields.TranslatedField(blank=True, help_text='Notes for this section', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('feature', models.ForeignKey(to='webplatformcompat.Feature', related_name='references')),
                ('section', models.ForeignKey(to='webplatformcompat.Section', related_name='references')),
            ],
            bases=(webplatformcompat.models.HistoryMixin, models.Model),
        ),
        migrations.AddField(
            model_name='historicalfeature',
            name='references',
            field=django_extensions.db.fields.json.JSONField(null=True, default='[]'),
        ),
        migrations.AlterField(
            model_name='historicalfeature',
            name='sections',
            field=django_extensions.db.fields.json.JSONField(null=True, default='[]'),
        ),
        migrations.AlterUniqueTogether(
            name='reference',
            unique_together=set([('feature', 'section')]),
        ),
        migrations.AlterOrderWithRespectTo(
            name='reference',
            order_with_respect_to='feature',
        ),
        migrations.AlterField(
            model_name='changeset',
            name='target_resource_type',
            field=models.CharField(max_length=12, blank=True, help_text='Type of target resource', choices=[('browsers', 'browsers'), ('features', 'features'), ('maturities', 'maturities'), ('references', 'references'), ('sections', 'sections'), ('specifications', 'specifications'), ('supports', 'supports'), ('versions', 'versions')]),
        ),
        migrations.AlterField(
            model_name='historicalsection',
            name='note',
            field=webplatformcompat.fields.TranslatedField(help_text='Notes for this section', blank=True, null=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
        ),
        migrations.AlterField(
            model_name='section',
            name='note',
            field=webplatformcompat.fields.TranslatedField(help_text='Notes for this section', blank=True, null=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)]),
        ),
    ]
