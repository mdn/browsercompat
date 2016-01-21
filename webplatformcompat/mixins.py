"""Mixins for DRF Viewsets.

This is modeled after DRF's mixins.py. However, the current strategy is to
declare the mixins in viewsets.py directly.
"""


class PartialPutMixin(object):
    """
    If content type is JSON API, treat PUT as a partial update.

    In Django REST Framework:
    - PUT is a full replacement
    - PATCH is a partial replacement
    In JSON API:
    - PUT is partial replacement with content type "application/vnd.api+json"
    - PATCH uses JSON Patch format with type "application/json-put+json"
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if request.content_type.startswith('application/vnd.api+json'):
            partial = True
        return super(PartialPutMixin, self).update(
            request, partial=partial, *args, **kwargs)
