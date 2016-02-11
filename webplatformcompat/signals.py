# -*- coding: utf-8 -*-
"""Signal handlers for API models."""

from __future__ import unicode_literals

from django.conf import settings
from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver

from .models import Feature, Section

cached_model_names = (
    'Browser', 'Feature', 'Maturity', 'Section', 'Specification',
    'Support', 'Version', 'User')


@receiver(
    m2m_changed, sender=Feature.sections.through,
    dispatch_uid='m2m_changed_feature_section')
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


@receiver(post_delete, dispatch_uid='post_delete_update_cache')
def post_delete_update_cache(sender, instance, **kwargs):
    name = sender.__name__
    if name in cached_model_names:
        delay_cache = getattr(instance, '_delay_cache', False)
        if not delay_cache:
            from .tasks import update_cache_for_instance
            update_cache_for_instance(name, instance.pk, instance)


@receiver(post_save, dispatch_uid='post_save_update_cache')
def post_save_update_cache(sender, instance, created, raw, **kwargs):
    if raw:
        return
    name = sender.__name__
    if name in cached_model_names:
        delay_cache = getattr(instance, '_delay_cache', False)
        if not delay_cache:
            from .tasks import update_cache_for_instance
            update_cache_for_instance(name, instance.pk, instance)


#
# New user signals
#
@receiver(
    post_save, sender=settings.AUTH_USER_MODEL,
    dispatch_uid='add_user_to_change_resource_group')
def add_user_to_change_resource_group(
        signal, sender, instance, created, raw, **kwargs):
    if created and not raw:
        from django.contrib.auth.models import Group
        instance.groups.add(Group.objects.get(name='change-resource'))
        if hasattr(instance, 'group_names'):
            del instance.group_names
        post_save_update_cache(sender, instance, created, raw, **kwargs)
