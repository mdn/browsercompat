# -*- coding: utf-8 -*-
"""API exceptions and exception handler."""

from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler as base_handler


class InvalidQueryParam(APIException):
    """The request contained a bad query parameter.

    JSON API v1.0 defines a structure (source/parameter) for specifying which
    query parameter was bad.
    http://jsonapi.org/format/1.0/#error-objects
    """

    detail_fmt = _('Query parameter "%(query_param)s" is invalid.')
    status_code = HTTP_400_BAD_REQUEST

    def __init__(self, query_param):
        """Initialize the exception with the bad query parameter."""
        self.parameter = query_param
        self.detail = self.detail_fmt % {'query_param': query_param}


class NotImplementedQueryParam(InvalidQueryParam):
    """Request contained an query parameter that is not implemented.

    JSON API v1.0 requires a 400 when the service doesn't support a documented
    query parameter, such as 'include':
    http://jsonapi.org/format/1.0/#fetching-includes
    """

    detail_fmt = _('Query parameter "%(query_param)s" is not implemented.')


def handler(exc, context):
    """
    Return the response that should be used for any given exception.

    If the v2 API is called, use the JSON API v1.0 exception handler.
    Otherwise, use the default Django REST Framework handler.
    """
    response = base_handler(exc, context)
    if response is not None:
        response.exc = exc
    return response
