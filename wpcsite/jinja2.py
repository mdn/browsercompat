"""Helper functions for Jinja2 templates."""
from __future__ import absolute_import

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ungettext
from jinja2 import Environment

from webplatformcompat.helpers import env as wp_env
from bcauth.helpers import env as bcauth_env
from mdn.helpers import env as mdn_env


def url(viewname, *args, **kwargs):
    return reverse(viewname, args=args, kwargs=kwargs)


def environment(**options):
    """Construct environment for jinja2 templates."""
    env = Environment(
        extensions=['jinja2.ext.i18n', 'jinja2.ext.autoescape'],
        trim_blocks=True,
        **options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url,
        '_': ugettext,
        'gettext': ugettext,
        'ngettext': ungettext,
    })
    for app_env in (wp_env, bcauth_env, mdn_env):
        for group, to_add in app_env.items():
            if group == 'globals':
                for name, value in to_add.items():
                    assert name not in env.globals
                    env.globals[name] = value
            else:
                assert group == 'filters', 'Unknown group {}'.format(group)
                for name, value in to_add.items():
                    assert name not in env.filters
                    env.filters[name] = value
    return env
