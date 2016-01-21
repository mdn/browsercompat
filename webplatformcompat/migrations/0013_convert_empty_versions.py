# -*- coding: utf-8 -*-
"""Convert blank version string to "current".

When a browser has supported a feature for a long time, it is unknown what
version added that support. Previously, this was modeled as a blank string
for the version. Now, it is modeled as the string "current" for the version.

See https://bugzilla.mozilla.org/show_bug.cgi?id=1160214
"""
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.db import migrations
from webplatformcompat.cache import Cache


def convert_empty_versions(apps, schema_editor):
    Version = apps.get_model('webplatformcompat', 'Version')
    # Database stores as empty string, API converts to null
    has_blank = Version.objects.filter(version='')
    has_bad_status = has_blank.exclude(status__in=('current', 'unknown'))
    if has_bad_status.exists():
        raise Exception(
            'Some versions with empty version strings have an unexpected'
            ' status. IDs:', list(has_bad_status.values_list('id', flat=True)))

    if has_blank.exists():
        print('\nConverting blank version.version to "current"...')
        Changeset = apps.get_model('webplatformcompat', 'Changeset')
        HistoricalVersion = apps.get_model(
            'webplatformcompat', 'HistoricalVersion')
        User = apps.get_model(settings.AUTH_USER_MODEL)
        superuser = User.objects.filter(
            is_superuser=True).order_by('id').first()
        assert superuser, 'Must be at least one superuser'
        cs = Changeset.objects.create(user=superuser)
        for version in has_blank:
            print('Version %d: Converting version to "current"' % version.id)

            # Update the instance
            version.version = 'current'
            version.status = 'current'
            version._delay_cache = True
            version.save()
            Cache().delete_all_versions('Version', version.id)

            # Create a historical version
            hs = HistoricalVersion(
                history_date=cs.created, history_changeset=cs,
                history_type='~',
                **dict((field.attname, getattr(version, field.attname))
                       for field in Version._meta.fields))
            hs.save()
        cs.close = True
        cs.save()


def warn_about_converted(apps, schema_editor):
    HistoricalVersion = apps.get_model(
        'webplatformcompat', 'HistoricalVersion')
    has_blank = HistoricalVersion.objects.filter(version='')
    if has_blank.exists():
        print('\nWARNING: version=<blank> used in past, not restored')


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0012_drop_support_support_never'),
    ]

    operations = [
        migrations.RunPython(convert_empty_versions, warn_about_converted)
    ]
