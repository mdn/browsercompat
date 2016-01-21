# -*- coding: utf-8 -*-
"""Add change-resource and delete-resource groups and related permissions."""
from __future__ import unicode_literals
from itertools import chain

from django.db import migrations

group_perms = {
    'change-resource': [
        'add_changeset',
        'change_changeset',
        'add_browser',
        'change_browser',
        'add_feature',
        'change_feature',
        'add_maturity',
        'change_maturity',
        'add_section',
        'change_section',
        'add_specification',
        'change_specification',
        'add_support',
        'change_support',
        'add_version',
        'change_version',
    ],
    'delete-resource': [
        'add_changeset',
        'change_changeset',
        'delete_browser',
        'delete_feature',
        'delete_maturity',
        'delete_section',
        'delete_specification',
        'delete_support',
        'delete_version',
    ]
}


def add_groups(apps, schema_editor, with_create_permissions=True):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    User = apps.get_model('auth', 'User')

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
            return add_groups(
                apps, schema_editor, with_create_permissions=False)
        else:
            raise

    for group_name in sorted(group_perms.keys()):
        group = Group.objects.create(name=group_name)
        perm_list = [
            perms[codename] for codename in group_perms[group_name]]
        group.permissions.add(*perm_list)

    change_group = Group.objects.get(name='change-resource')
    for user in User.objects.all():
        user.groups.add(change_group)


def drop_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')

    change_group = Group.objects.get(name='change-resource')
    for user in User.objects.all():
        user.groups.remove(change_group)

    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=list(group_perms.keys())).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('webplatformcompat', '0004_drop_field_feature_mdn_path'),
    ]

    operations = [
        migrations.RunPython(add_groups, drop_groups),
    ]
