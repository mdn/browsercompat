"""Helper functions for Jinja2 templates."""
from __future__ import absolute_import

from django.contrib.messages import get_messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse

from jinja2.ext import Extension


def url(viewname, *args, **kwargs):
    return reverse(viewname, args=args, kwargs=kwargs)


def static(*args, **kwargs):
    return staticfiles_storage.url(*args, **kwargs)


class WPCExtension(Extension):
    def __init__(self, environment):
        super(WPCExtension, self).__init__(environment)
        environment.globals['url'] = url
        environment.globals['static'] = static
        environment.globals['get_messages'] = get_messages
