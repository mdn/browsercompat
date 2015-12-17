# -*- coding: utf-8 -*-
"""Renderers for the API."""
from __future__ import unicode_literals

from collections import OrderedDict
from json import loads

from django.template import loader, Context
from django.utils import translation
from rest_framework.renderers import BrowsableAPIRenderer as BaseAPIRenderer
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT


class BrowsableAPIRenderer(BaseAPIRenderer):
    """Jinja2 renderer used to self-document the API."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render the HTML for the browsable API representation.

        Same as base renderer, but uses a plain dict and request instead of
        constructing a RequestContext.
        """
        self.accepted_media_type = accepted_media_type or ''
        self.renderer_context = renderer_context or {}

        template = loader.get_template(self.template)
        context = self.get_context(data, accepted_media_type, renderer_context)
        ret = template.render(context, context.get('request'))

        # Munge DELETE Response code to allow us to return content
        # (Do this *after* we've rendered the template so that we include
        # the normal deletion response code in the output)
        response = renderer_context['response']
        if response.status_code == HTTP_204_NO_CONTENT:  # pragma: no cover
            response.status_code = HTTP_200_OK

        return ret


class BaseJsonApiTemplateHTMLRenderer(TemplateHTMLRenderer):
    """Render to a template, but use JSON API format as context."""

    json_api_renderer_class = None  # Set by namespace-specific implementation

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Generate JSON API representation, as well as collection."""
        # Set the context to the JSON API represention
        assert self.json_api_renderer_class
        json_api_renderer = self.json_api_renderer_class()
        json_api = json_api_renderer.render(
            data, accepted_media_type, renderer_context)
        context = loads(
            json_api.decode('utf-8'), object_pairs_hook=OrderedDict)

        # Is it an error?
        if 'errors' in context:
            error_context = Context(context)
            return super(BaseJsonApiTemplateHTMLRenderer, self).render(
                error_context, accepted_media_type, renderer_context)

        # Make namespace-specific customizations
        self.customize_context(context)

        # Add language
        request = renderer_context['request']
        lang = request.GET.get('lang', translation.get_language())
        context['lang'] = lang

        # Render HTML template w/ context
        return super(BaseJsonApiTemplateHTMLRenderer, self).render(
            context, accepted_media_type, renderer_context)

    def resolve_context(self, data, request, response):
        """Resolve context without a RequestContext."""
        if response.exception:
            data['status_code'] = response.status_code
        return data
