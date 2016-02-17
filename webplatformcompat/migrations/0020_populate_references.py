# -*- coding: utf-8 -*-
"""Populate References table from Sections.

Also:
* Ensure each Reference has a current_history
* Convert null HistoricalFeature.references to empty list
"""
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

from webplatformcompat.cache import Cache


def create_changeset(apps):
    """Create a changeset for the migration."""
    Changeset = apps.get_model('webplatformcompat', 'Changeset')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    superuser = User.objects.filter(
        is_superuser=True).order_by('id').first()
    assert superuser, 'Must be at least one superuser'
    changeset = Changeset.objects.create(user=superuser)
    return changeset


def populate_references(apps, schema_editor, with_create_permissions=True):
    """Copy data from sections to references."""
    Feature = apps.get_model('webplatformcompat', 'Feature')
    Reference = apps.get_model('webplatformcompat', 'Reference')
    HistoricalReference = apps.get_model(
        'webplatformcompat', 'HistoricalReference')
    HistoricalFeature = apps.get_model(
        'webplatformcompat', 'HistoricalFeature')
    changeset = None
    cache = Cache()

    for feature in Feature.objects.all():
        if feature.sections.exists():
            new_reference_order = []
            old_reference_order = feature.get_reference_order()
            for section in feature.sections.all():
                # Trim empty notes
                note = section.note
                if note == {'en': ''}:
                    note = None

                # Add Reference for M2M Feature/Section relationships
                changed = ''
                try:
                    reference = Reference.objects.get(
                        feature=feature, section=section)
                except Reference.DoesNotExist:
                    reference = Reference.objects.create(
                        feature=feature, section=section, note=note)
                    changed = '+'
                else:
                    if reference.note != note:
                        changed = '~'
                        reference.note = note
                        reference.save()
                        cache.delete_all_versions('Reference', reference.pk)
                        cache.delete_all_versions('Section', section.pk)

                # Add at least one HistoricalReference entry
                if changed:
                    changeset = changeset or create_changeset(apps)
                    HistoricalReference.objects.create(
                        history_date=changeset.created,
                        history_changeset=changeset,
                        history_type=changed,
                        **dict(
                            (field.attname, getattr(reference, field.attname))
                            for field in Reference._meta.fields))

                new_reference_order.append(reference.id)

            # Update Feature.references order if needed
            if new_reference_order != old_reference_order:
                feature.set_reference_order(new_reference_order)
                cache.delete_all_versions('Feature', feature.pk)

    # Populate null reference lists in historical references
    HistoricalFeature.objects.filter(
        references__isnull=True).update(references='[]')


def populate_sections(apps, schema_editor):
    """Copy data from references back to sections."""
    Feature = apps.get_model('webplatformcompat', 'Feature')
    Reference = apps.get_model('webplatformcompat', 'Reference')
    Section = apps.get_model('webplatformcompat', 'Section')
    HistoricalSection = apps.get_model(
        'webplatformcompat', 'HistoricalSection')
    HistoricalFeature = apps.get_model(
        'webplatformcompat', 'HistoricalFeature')
    changeset = None
    cache = Cache()

    for feature in Feature.objects.all():
        if feature.references.exists():
            reference_order = feature.get_reference_order()
            old_section_order = feature.sections.values_list('id', flat=True)
            new_section_order = []

            # Add M2M Feature/Section relationship for each Reference
            for reference_id in reference_order:
                reference = Reference.objects.get(id=reference_id)
                section = reference.section

                if section.note != reference.note:
                    section.note = reference.note
                    section.save()
                    cache.delete_all_versions('Section', section.pk)
                    changeset = changeset or create_changeset(apps)
                    HistoricalSection.objects.create(
                        history_date=changeset.created,
                        history_changeset=changeset,
                        history_type='~',
                        **dict((field.attname, getattr(section, field.attname))
                               for field in Section._meta.fields))

                new_section_order.append(section.id)

            # Update Feature.sections order if needed
            if new_section_order != old_section_order:
                feature.sections = new_section_order
                cache.delete_all_versions('Feature', feature.pk)

    # Return empty Feature.resources lists to null
    HistoricalFeature.objects.filter(references='[]').update(references=None)


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0019_add_reference_permissions'),
    ]

    operations = [
        migrations.RunPython(populate_references, populate_sections)
    ]
