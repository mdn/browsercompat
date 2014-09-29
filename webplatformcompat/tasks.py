from celery import shared_task

from .cache import Cache


@shared_task(ignore_result=True)
def update_cache_for_instance(
        model_name, instance_pk, instance=None, version=None):
    cache = Cache()
    invalid = cache.update_instance(model_name, instance_pk, instance, version)
    for invalid_name, invalid_pk, invalid_version in invalid:
        update_cache_for_instance.delay(
            invalid_name, invalid_pk, version=invalid_version)
