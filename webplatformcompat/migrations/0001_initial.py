# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations
import webplatformcompat.validators
import webplatformcompat.fields
import django_extensions.db.fields
import django_extensions.db.fields.json
import mptt.fields
import sortedm2m.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug.', unique=True)),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Branding name of browser, client, or platform.', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Extended information about browser, client, or platform.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Changeset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('closed', models.BooleanField(default=False, help_text='Is the changeset closed to new changes?')),
                ('target_resource_type', models.CharField(blank=True, help_text='Type of target resource', max_length=12, choices=[('browsers', 'browsers'), ('features', 'features'), ('maturities', 'maturities'), ('sections', 'sections'), ('specifications', 'specifications'), ('supports', 'supports'), ('versions', 'versions')])),
                ('target_resource_id', models.PositiveIntegerField(default=0, help_text='ID of target resource')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug.', unique=True)),
                ('mdn_path', models.CharField(help_text='The path to the page on MDN that this feature was first scraped from.  May be used in UX or for debugging import scripts.', max_length=255, blank=True)),
                ('experimental', models.BooleanField(default=False, help_text='True if a feature is considered experimental, such as being non-standard or part of an non-ratified spec.')),
                ('standardized', models.BooleanField(default=True, help_text='True if a feature is described in a standards-track spec, regardless of the spec\u2019s maturity.')),
                ('stable', models.BooleanField(default=True, help_text='True if a feature is considered suitable for production websites.')),
                ('obsolete', models.BooleanField(default=False, help_text='True if a feature should not be used in new development.')),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Feature name, in canonical or localized form.', validators=[webplatformcompat.validators.LanguageDictValidator(True)])),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='webplatformcompat.Feature', help_text='Feature set that contains this feature', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalBrowser',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug.')),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Branding name of browser, client, or platform.', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Extended information about browser, client, or platform.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_browsers', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical browser',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalFeature',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug.')),
                ('mdn_path', models.CharField(help_text='The path to the page on MDN that this feature was first scraped from.  May be used in UX or for debugging import scripts.', max_length=255, blank=True)),
                ('experimental', models.BooleanField(default=False, help_text='True if a feature is considered experimental, such as being non-standard or part of an non-ratified spec.')),
                ('standardized', models.BooleanField(default=True, help_text='True if a feature is described in a standards-track spec, regardless of the spec\u2019s maturity.')),
                ('stable', models.BooleanField(default=True, help_text='True if a feature is considered suitable for production websites.')),
                ('obsolete', models.BooleanField(default=False, help_text='True if a feature should not be used in new development.')),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Feature name, in canonical or localized form.', validators=[webplatformcompat.validators.LanguageDictValidator(True)])),
                ('parent_id', models.IntegerField(help_text='Feature set that contains this feature', null=True, db_index=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('sections', django_extensions.db.fields.json.JSONField(default='[]')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_features', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical feature',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalMaturity',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug, sourced from the KumaScript macro Spec2')),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of maturity', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_maturities', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical maturity',
                'verbose_name_plural': 'historical_maturities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalSection',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('specification_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('number', webplatformcompat.fields.TranslatedField(help_text='Section number', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of section, without section number', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('subpath', webplatformcompat.fields.TranslatedField(help_text='A subpage (possible with an #anchor) to get to the subsection in the specification.', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Notes for this section', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('_order', models.IntegerField(editable=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_sections', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical section',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalSpecification',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('maturity_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug')),
                ('mdn_key', models.CharField(help_text='Key used in the KumaScript macro SpecName', max_length=30, blank=True)),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of specification', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('uri', webplatformcompat.fields.TranslatedField(help_text='Specification URI, without subpath and anchor', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_specifications', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical specification',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalSupport',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('version_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('feature_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('support', models.CharField(default='yes', help_text='Does the browser version support this feature?', max_length=10, choices=[('yes', 'yes'), ('no', 'no'), ('partial', 'partial'), ('unknown', 'unknown'), ('never', 'never')])),
                ('prefix', models.CharField(help_text='Prefix to apply to the feature name.', max_length=20, blank=True)),
                ('prefix_mandatory', models.BooleanField(default=False, help_text='Is the prefix required?')),
                ('alternate_name', models.CharField(help_text='Alternate name for this feature.', max_length=50, blank=True)),
                ('alternate_mandatory', models.BooleanField(default=False, help_text='Is the alternate name required?')),
                ('requires_config', models.CharField(help_text='A configuration string to enable the feature.', max_length=100, blank=True)),
                ('default_config', models.CharField(help_text='The configuration string in the shipping browser.', max_length=100, blank=True)),
                ('protected', models.BooleanField(default=False, help_text="True if feature requires additional steps to enable in order to protect the user's security or privacy.")),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Short note on support, designed for inline display.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('footnote', webplatformcompat.fields.TranslatedField(help_text='Long note on support, designed for display after a compatiblity table, in MDN wiki format.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_supports', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical support',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalVersion',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('browser_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('version', models.CharField(help_text='Version string.', max_length=20, blank=True)),
                ('release_day', models.DateField(help_text='Day of release to public, ISO 8601 format.', null=True, blank=True)),
                ('retirement_day', models.DateField(help_text='Day this version stopped being supported, ISO 8601 format.', null=True, blank=True)),
                ('status', models.CharField(default='unknown', max_length=15, choices=[('unknown', 'unknown'), ('current', 'current'), ('future', 'future'), ('retired', 'retired'), ('beta', 'beta'), ('retired beta', 'retired beta')])),
                ('release_notes_uri', webplatformcompat.fields.TranslatedField(help_text='URI of release notes.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Notes about this version.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('_order', models.IntegerField(editable=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_changeset', models.ForeignKey(related_name='historical_versions', to='webplatformcompat.Changeset')),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical version',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Maturity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug, sourced from the KumaScript macro Spec2', unique=True)),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of maturity', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
            ],
            options={
                'verbose_name_plural': 'maturities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', webplatformcompat.fields.TranslatedField(help_text='Section number', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of section, without section number', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('subpath', webplatformcompat.fields.TranslatedField(help_text='A subpage (possible with an #anchor) to get to the subsection in the specification.', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Notes for this section', blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Unique, human-friendly slug', unique=True)),
                ('mdn_key', models.CharField(help_text='Key used in the KumaScript macro SpecName', max_length=30, blank=True)),
                ('name', webplatformcompat.fields.TranslatedField(help_text='Name of specification', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('uri', webplatformcompat.fields.TranslatedField(help_text='Specification URI, without subpath and anchor', validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('maturity', models.ForeignKey(related_name='specifications', to='webplatformcompat.Maturity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('support', models.CharField(default='yes', help_text='Does the browser version support this feature?', max_length=10, choices=[('yes', 'yes'), ('no', 'no'), ('partial', 'partial'), ('unknown', 'unknown'), ('never', 'never')])),
                ('prefix', models.CharField(help_text='Prefix to apply to the feature name.', max_length=20, blank=True)),
                ('prefix_mandatory', models.BooleanField(default=False, help_text='Is the prefix required?')),
                ('alternate_name', models.CharField(help_text='Alternate name for this feature.', max_length=50, blank=True)),
                ('alternate_mandatory', models.BooleanField(default=False, help_text='Is the alternate name required?')),
                ('requires_config', models.CharField(help_text='A configuration string to enable the feature.', max_length=100, blank=True)),
                ('default_config', models.CharField(help_text='The configuration string in the shipping browser.', max_length=100, blank=True)),
                ('protected', models.BooleanField(default=False, help_text="True if feature requires additional steps to enable in order to protect the user's security or privacy.")),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Short note on support, designed for inline display.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('footnote', webplatformcompat.fields.TranslatedField(help_text='Long note on support, designed for display after a compatiblity table, in MDN wiki format.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('feature', models.ForeignKey(related_name='supports', to='webplatformcompat.Feature')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(help_text='Version string.', max_length=20, blank=True)),
                ('release_day', models.DateField(help_text='Day of release to public, ISO 8601 format.', null=True, blank=True)),
                ('retirement_day', models.DateField(help_text='Day this version stopped being supported, ISO 8601 format.', null=True, blank=True)),
                ('status', models.CharField(default='unknown', max_length=15, choices=[('unknown', 'unknown'), ('current', 'current'), ('future', 'future'), ('retired', 'retired'), ('beta', 'beta'), ('retired beta', 'retired beta')])),
                ('release_notes_uri', webplatformcompat.fields.TranslatedField(help_text='URI of release notes.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('note', webplatformcompat.fields.TranslatedField(help_text='Notes about this version.', null=True, blank=True, validators=[webplatformcompat.validators.LanguageDictValidator(False)])),
                ('browser', models.ForeignKey(related_name='versions', to='webplatformcompat.Browser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name='version',
            order_with_respect_to='browser',
        ),
        migrations.AddField(
            model_name='support',
            name='version',
            field=models.ForeignKey(related_name='supports', to='webplatformcompat.Version'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='support',
            unique_together=set([('version', 'feature')]),
        ),
        migrations.AddField(
            model_name='section',
            name='specification',
            field=models.ForeignKey(related_name='sections', to='webplatformcompat.Specification'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='section',
            order_with_respect_to='specification',
        ),
        migrations.AddField(
            model_name='feature',
            name='sections',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, related_name='features', to='webplatformcompat.Section'),
            preserve_default=True,
        ),
    ]
