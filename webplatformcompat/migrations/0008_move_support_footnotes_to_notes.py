# -*- coding: utf-8 -*-
"""Move support.footnotes into the support.notes field.

Inline notes are being dropped, so that there is a single place to specify
human-friendly notes. Rather than using "footnote" for the combined field,
"note" will be the one field name. Current footnote data is moved to the
notes field, unless both are populated, which will halt the migration.

See https://bugzilla.mozilla.org/show_bug.cgi?id=1128519
"""
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import migrations
from webplatformcompat.cache import Cache


def move_footnotes(apps, schema_editor):
    Support = apps.get_model('webplatformcompat', 'Support')
    has_footnote = Support.objects.exclude(
        footnote__isnull=True).exclude(footnote='{}')
    has_both = has_footnote.exclude(note__isnull=True).exclude(note='{}')
    if has_both.exists():
        raise Exception(
            'Some supports have both note and footnote set. IDs:',
            list(has_both.values_list('id', flat=True)))

    if has_footnote.exists():
        print('\nMoving support.footnotes to notes...')
        Changeset = apps.get_model('webplatformcompat', 'Changeset')
        HistoricalSupport = apps.get_model(
            'webplatformcompat', 'HistoricalSupport')
        User = apps.get_model(settings.AUTH_USER_MODEL)
        superuser = User.objects.filter(
            is_superuser=True).order_by('id').first()
        assert superuser, 'Must be at least one superuser'
        cs = Changeset.objects.create(user=superuser)
        for support in has_footnote:
            print('Support %d: Moving footnote "%s"' %
                  (support.id, repr(support.footnote)[:50]))

            # Update the instance
            support.note = support.footnote
            support.footnote = {}
            support._delay_cache = True
            support.save()

            # Manually clear the cache
            cache = Cache()
            if cache.cache:
                for version in cache.versions:
                    key = cache.key_for(version, 'Support', support.id)
                    cache.cache.delete(key)

            # Create a historical support
            hs = HistoricalSupport(
                history_date=cs.created, history_changeset=cs,
                history_type='~',
                **dict((field.attname, getattr(support, field.attname))
                       for field in Support._meta.fields))
            hs.save()
        cs.close = True
        cs.save()


def warn_about_moved_footnotes(apps, schema_editor):
    Support = apps.get_model('webplatformcompat', 'Support')
    has_note = Support.objects.exclude(note__isnull=True).exclude(note='{}')
    if has_note.exists():
        print('\nWARNING: footnotes may have been merged into notes')


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0007_update_historical_models_for_1_5_4'),
    ]

    operations = [
        migrations.RunPython(move_footnotes, warn_about_moved_footnotes)
    ]
