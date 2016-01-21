"""API background tasks."""
from celery import shared_task
from django.conf import settings

from .cache import Cache


@shared_task(ignore_result=True)
def update_cache_for_instance(
        model_name, instance_pk, instance=None, version=None,
        update_only=False):
    cache = Cache()
    invalid = cache.update_instance(
        model_name, instance_pk, instance, version, update_only=update_only)
    DRF_INSTANCE_CACHE_POPULATE_COLD = getattr(
        settings, 'DRF_INSTANCE_CACHE_POPULATE_COLD', True)
    for invalid_name, invalid_pk, invalid_version in invalid:
        update_cache_for_instance.delay(
            invalid_name, invalid_pk, version=invalid_version,
            update_only=not DRF_INSTANCE_CACHE_POPULATE_COLD)
