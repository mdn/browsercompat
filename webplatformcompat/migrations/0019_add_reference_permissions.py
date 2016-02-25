# -*- coding: utf-8 -*-
"""Add API permissions for reference instances."""
from __future__ import unicode_literals
from itertools import chain

from django.db import migrations

group_perms = {
    'change-resource': [
        'add_reference',
        'change_reference',
    ],
    'delete-resource': [
        'delete_reference',
    ]
}


def add_permissions(apps, schema_editor, with_create_permissions=True):
    """Add resource permissions to API groups."""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    try:
        perms = dict(
            [(codename, Permission.objects.get(codename=codename))
             for codename in set(chain(*group_perms.values()))])
    except Permission.DoesNotExist:
        if with_create_permissions:
            # create_permissions runs in the post_migrate signal, at the end of
            # all migrations. If migrating a fresh database (such as during
            # tests), then manually run create_permissions.
            from django.contrib.auth.management import create_permissions
            assert not getattr(apps, 'models_module', None)
            apps.models_module = True
            create_permissions(apps, verbosity=0)
            apps.models_module = None
            return add_permissions(
                apps, schema_editor, with_create_permissions=False)
        else:
            raise

    for group_name in sorted(group_perms.keys()):
        group = Group.objects.get(name=group_name)
        perm_list = [
            perms[codename] for codename in group_perms[group_name]]
        group.permissions.add(*perm_list)


def drop_permissions(apps, schema_editor):
    """Drop References permissions."""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    perms = dict()
    for codename in set(chain(*group_perms.values())):
        try:
            permission = Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            pass
        else:
            perms[codename] = permission

    for group_name in sorted(group_perms.keys()):
        group = Group.objects.get(name=group_name)
        perm_list = [
            perms[codename] for codename in group_perms[group_name]]
        group.permissions.remove(*perm_list)


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0018_add_resources_table'),
    ]

    operations = [
        migrations.RunPython(add_permissions, drop_permissions)
    ]
