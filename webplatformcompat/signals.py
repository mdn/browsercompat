# -*- coding: utf-8 -*-
"""Signal handlers for API models."""

from __future__ import unicode_literals

from django.contrib.auth.models import Group

from .tasks import update_cache_for_instance


def add_user_to_change_resource_group(
        signal, sender, instance, created, raw, **kwargs):
    """Add change-resource permission to new users."""
    if created and not raw:
        instance.groups.add(Group.objects.get(name='change-resource'))


def post_delete_update_cache(sender, instance, **kwargs):
    """Invalidate the cache when an instance is deleted."""
    name = sender.__name__
    delay_cache = getattr(instance, '_delay_cache', False)
    if not delay_cache:
        update_cache_for_instance(name, instance.pk, instance)


def post_save_changeset(sender, instance, created, raw, **kwargs):
    """Invalidate the user cache after a changeset is created."""
    if raw or not created:
        return
    update_cache_for_instance('User', instance.user.pk, instance.user)


def post_save_update_cache(sender, instance, created, raw, **kwargs):
    """Invalidate the cache when an instance is created or updated."""
    if raw:
        return
    name = sender.__name__
    if name == 'User' and created:
        return
    delay_cache = getattr(instance, '_delay_cache', False)
    if not delay_cache:
        update_cache_for_instance(name, instance.pk, instance)
