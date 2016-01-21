# -*- coding: utf-8 -*-
"""Convert support.support="never" to "no".

"never" was used to signal that the browser maintainer had decided not to
support a feature, and was usually supported by a WON'T FIX ticket. This
changes the API strategy to support="no", and (optionally) linking to
supporting documentation in a note.

See https://bugzilla.mozilla.org/show_bug.cgi?id=1170209
"""
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.db import migrations
from webplatformcompat.cache import Cache


def convert_support_never(apps, schema_editor):
    Support = apps.get_model('webplatformcompat', 'Support')
    has_never = Support.objects.filter(support='never')

    if has_never.exists():
        print('\nConverting support.support="never" to "no"...')
        Changeset = apps.get_model('webplatformcompat', 'Changeset')
        HistoricalSupport = apps.get_model(
            'webplatformcompat', 'HistoricalSupport')
        User = apps.get_model(settings.AUTH_USER_MODEL)
        superuser = User.objects.filter(
            is_superuser=True).order_by('id').first()
        assert superuser, 'Must be at least one superuser'
        cs = Changeset.objects.create(user=superuser)
        for support in has_never.iterator():
            print('Support %d: Converting support to no' % support.id)

            # Update the instance
            support.support = 'no'
            support._delay_cache = True
            support.save()
            Cache().delete_all_versions('Support', support.id)

            # Create a historical support
            hs = HistoricalSupport(
                history_date=cs.created, history_changeset=cs,
                history_type='~',
                **dict((field.attname, getattr(support, field.attname))
                       for field in Support._meta.fields))
            hs.save()
        cs.close = True
        cs.save()


def warn_about_converted_never(apps, schema_editor):
    HistoricalSupport = apps.get_model(
        'webplatformcompat', 'HistoricalSupport')
    has_never = HistoricalSupport.objects.filter(support='never')
    if has_never.exists():
        print('\nWARNING: support=never used in past, not restored')


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0010_simple_history_updates'),
    ]

    operations = [
        migrations.RunPython(convert_support_never, warn_about_converted_never)
    ]
