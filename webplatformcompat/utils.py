"""API utilty functions."""
from rest_framework.views import get_view_name as drf_get_view_name


def get_view_name(view_cls, suffix=None):
    name = drf_get_view_name(view_cls, suffix=None)
    if name == 'Api Root':
        return 'API Root'
    else:
        return name
