# -*- coding: utf-8 -*-
"""Signal handlers for API models."""

from __future__ import unicode_literals

from .models import Feature, Section


def add_user_to_change_resource_group(
        signal, sender, instance, created, raw, **kwargs):
    """Add change-resource permission to new users."""
    if created and not raw:
        from django.contrib.auth.models import Group
        instance.groups.add(Group.objects.get(name='change-resource'))


def feature_sections_changed_update_order(
        sender, instance, action, reverse, model, pk_set, **kwargs):
    """Maintain feature.section_order."""
    if action not in ('post_add', 'post_remove', 'post_clear'):
        # post_clear is not handled, because clear is called in
        # django.db.models.fields.related.ReverseManyRelatedObjects.__set__
        # before setting the new order
        return
    if getattr(instance, '_delay_cache', False):
        return

    if model == Section:
        assert type(instance) == Feature
        features = [instance]
        if pk_set:
            sections = list(Section.objects.filter(pk__in=pk_set))
        else:
            sections = []
    else:
        if pk_set:
            features = list(Feature.objects.filter(pk__in=pk_set))
        else:
            features = []
        sections = [instance]

    from .tasks import update_cache_for_instance
    for feature in features:
        update_cache_for_instance('Feature', feature.pk, feature)
    for section in sections:
        update_cache_for_instance('Section', section.pk, section)


def post_delete_update_cache(sender, instance, **kwargs):
    """Invalidate the cache when an instance is deleted."""
    name = sender.__name__
    delay_cache = getattr(instance, '_delay_cache', False)
    if not delay_cache:
        from .tasks import update_cache_for_instance
        update_cache_for_instance(name, instance.pk, instance)


def post_save_update_cache(sender, instance, created, raw, **kwargs):
    """Invalidate the cache when an instance is created or updated."""
    if raw:
        return
    name = sender.__name__
    if name == 'User' and created:
        return
    delay_cache = getattr(instance, '_delay_cache', False)
    if not delay_cache:
        from .tasks import update_cache_for_instance
        update_cache_for_instance(name, instance.pk, instance)
