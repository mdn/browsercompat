# -*- coding: utf-8 -*-
"""Application configuration."""
from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class WebPlatformCompatConfig(AppConfig):
    """Configuration for the webplatformcompat app."""

    name = 'webplatformcompat'
    verbose_name = 'WebPlatformCompat'

    def ready(self):
        """Register signal handlers when models are loaded."""
        super(WebPlatformCompatConfig, self).ready()
        from django.contrib.auth.models import User
        from webplatformcompat.history import Changeset
        from webplatformcompat.models import (
            Browser, Feature, Maturity, Reference, Section, Specification,
            Support, Version)
        from webplatformcompat.signals import (
            add_user_to_change_resource_group,
            post_delete_update_cache,
            post_save_changeset,
            post_save_update_cache)

        # Add default API permissions to new users
        post_save.connect(
            add_user_to_change_resource_group,
            sender=User,
            dispatch_uid='add_user_to_change_resource_group')

        # Invalidate instance cache on model changes
        for model in (
                Browser, Feature, Maturity, Reference, Section,
                Specification, Support, Version, User):
            name = model.__name__
            post_delete.connect(
                post_delete_update_cache,
                sender=model,
                dispatch_uid='post_delete_update_cache_%s' % name)
            post_save.connect(
                post_save_update_cache,
                sender=model,
                dispatch_uid='post_save_update_cache_%s' % name)

        # Invalidate user instance cache on changeset creation
        post_save.connect(
            post_save_changeset,
            sender=Changeset,
            dispatch_uid='post_save_changeset')
