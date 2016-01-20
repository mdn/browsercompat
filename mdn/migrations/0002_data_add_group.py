# -*- coding: utf-8 -*-
"""Add import-mdn group and related permission."""
from __future__ import unicode_literals
from itertools import chain

from django.db import migrations

group_perms = {
    'import-mdn': [
        'add_featurepage',
        'change_featurepage',
        'add_feature',
        'change_feature',
    ],
}


def add_groups(apps, schema_editor, with_create_permissions=True):
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
            return add_groups(
                apps, schema_editor, with_create_permissions=False)
        else:
            raise

    for group_name in sorted(group_perms.keys()):
        group = Group.objects.create(name=group_name)
        perm_list = [
            perms[codename] for codename in group_perms[group_name]]
        group.permissions.add(*perm_list)


def drop_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=list(group_perms.keys())).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_groups, drop_groups),
    ]
