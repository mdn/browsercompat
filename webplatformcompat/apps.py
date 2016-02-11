# -*- coding: utf-8 -*-
"""Application configuration."""
from django.apps import AppConfig


class WebPlatformCompatConfig(AppConfig):
    name = 'webplatformcompat'
    verbose_name = 'WebPlatformCompat'

    def ready(self):
        super(WebPlatformCompatConfig, self).ready()
        import webplatformcompat.signals
        assert webplatformcompat.signals, 'Failed to make flake8 happy'
