"""Helper functions for Jinja2 templates

This file is loaded by jingo and must be named helper.py
"""

from django.contrib.staticfiles.templatetags.staticfiles import static

import jingo

jingo.register.function(static)
