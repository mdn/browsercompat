# -*- coding: utf-8 -*-
"""Renderers for the API."""
from __future__ import unicode_literals

from collections import OrderedDict
from json import loads

from django.template import loader, Context
from django.utils import translation

from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.renderers import BrowsableAPIRenderer as BaseAPIRenderer
from rest_framework.utils.serializer_helpers import ReturnList
from rest_framework.status import (
    HTTP_200_OK, HTTP_204_NO_CONTENT, is_client_error, is_server_error)
from rest_framework.utils.encoders import JSONEncoder


class JsonApiRC1Renderer(JSONRenderer):
    """JSON API Release Candidate 1 (RC1) render."""

    dict_class = OrderedDict
    encoder_class = JSONEncoder
    media_type = 'application/vnd.api+json'
    PAGINATION_KEYS = ('count', 'next', 'previous', 'results')

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Convert native DRF data to JSON API RC1.

        The four expected kinds of data are:
        - No data (maybe in response to 204 No Content)
        - Error data (status code is 4xx or 5xx)
        - Standard data (with serializer and fields_extra)
        - Paginated data
        """
        response = renderer_context['response']
        request = renderer_context['request']
        fields_extra = renderer_context.get('fields_extra')
        status_code = response and response.status_code
        is_err = is_client_error(status_code) or is_server_error(status_code)
        if data is None:
            converted = None
        elif is_err:
            converted = self.convert_error(data, status_code)
        elif self.is_paginated(data):
            converted = self.convert_paginated(data, request)
        elif request and request.method == 'OPTIONS':
            converted = {'meta': data}
        else:
            main_resource = fields_extra['id']['resource']
            converted = self.convert_standard(
                data, fields_extra, main_resource, request)

        renderer_context["indent"] = 4
        return super(JsonApiRC1Renderer, self).render(
            data=converted, renderer_context=renderer_context)

    def convert_error(self, data, status_code):
        """Convert error responses to JSON API RC1 format.

        Error responses are dictionaries. Simple Django errors, like permision
        denied errors, have a single key 'detail'. Field validation errors
        have the field name as the key, and a list of error strings. Errors on
        nested resources appear under the '_view_extra' key.

        JSON API RC1 specifies that errors appear as a dictionary with the
        key 'errors', and the value as a list of error dictionaries, such as:
        {"errors": [
            {"detail": "Error string",
             "path": "/attribute",
             "status_code": 400
            }]
        }
        """
        errors = []
        for name, value in data.items():
            if name == 'detail':
                fmt_error = self.dict_class((
                    ('detail', value),
                    ('status', str(status_code)),
                ))
                errors.append(fmt_error)
            elif name == '_view_extra':
                for rname, error_dict in value.items():
                    assert rname != 'meta', (
                        'meta errors not allowed in _view_extra errors.')
                    for seq, seq_errors in error_dict.items():
                        if seq is None:
                            # TODO: diagnose how subject feature errors are
                            # getting into view_extra.
                            seq = "subject"
                        for fieldname, error_list in seq_errors.items():
                            path = '/linked.%s.%s.%s' % (rname, seq, fieldname)
                            assert isinstance(error_list, list), (
                                'At %s, expecting a list, not "%s".'
                                % (path, error_list))
                            for error in error_list:
                                fmt_error = self.dict_class((
                                    ('detail', error),
                                    ('path', path),
                                    ('status', str(status_code)),
                                ))
                                errors.append(fmt_error)
            else:
                for error in value:
                    fmt_error = self.dict_class((
                        ('status', str(status_code)),
                        ('detail', error),
                        ('path', '/%s' % name),
                    ))
                    errors.append(fmt_error)
        assert errors, "No errors found in %s." % data
        return self.dict_class((('errors', errors),))

    def convert_standard(self, data, fields_extra, main_resource, request):
        """Convert a standard data item to RC1 format.

        Keyword Arguments:
        data - A dictionary-like object
        fields_extra - Field metadata, keyed by field name
        main_resource - The name of the resource key
        request - Used to generate full URLs
        """
        attributes = self.dict_class()
        link_ids = self.dict_class()
        link_patterns = self.dict_class()
        linked = self.dict_class()
        meta = self.dict_class()

        for name, value in data.items():
            field_extra = fields_extra.get(name, {})
            link = field_extra.get('link')
            attr_name = field_extra.get('name', name)
            if link:
                link_pattern, link_id = self.convert_link(
                    name, value, field_extra, main_resource, request)
                if link_pattern:
                    link_ids[attr_name] = link_id
                    pattern_name = "%s.%s" % (main_resource, attr_name)
                    link_patterns[pattern_name] = link_pattern
                else:
                    attributes[attr_name] = link_id
            elif name == '_view_extra':
                meta.update(value.pop('meta', {}))
                for ve_key, ve_list in value.items():
                    converted_list, resource = self.convert_list(
                        ve_list, request)
                    assert resource == ve_key, (
                        "%s != %s" % (resource, ve_key))
                    linked[ve_key] = converted_list[resource]
                    link_patterns.update(converted_list.get('links', {}))
            else:
                attributes[attr_name] = value

        converted = self.dict_class(((main_resource, attributes),))
        if link_ids:
            converted[main_resource]['links'] = link_ids
        if link_patterns:
            converted['links'] = link_patterns
        if linked:
            converted['linked'] = linked
        if meta:
            converted['meta'] = meta
        return converted

    def convert_paginated(self, data, request):
        """Convert paginated data to JSON API RC1.

        The pagination data is moved to the "meta" key, and the
        paginated "results" are split into resources and link data.
        """
        converted, resource = self.convert_list(data['results'], request)
        pagination = self.dict_class((
            ('previous', data['previous']),
            ('next', data['next']),
            ('count', data['count']),
        ))
        converted['meta'] = self.dict_class((
            ('pagination', self.dict_class((
                (resource, pagination),
            ))),
        ))
        return converted

    def convert_list(self, return_list, request):
        """Convert a ReturnList to JSON API RC1 format.

        The list data is moved under the resource name, and the link metadata
        is collected under the "links" key, using field data from the
        ReturnList's attached ListSerializer, and using the request to build
        full URLs.
        """
        assert isinstance(return_list, ReturnList), (
            "Should be ReturnList (for serializer data), is %s" %
            type(return_list))
        serializer = return_list.serializer.child
        fields_extra = serializer.get_fields_extra()
        main_resource = fields_extra['id']['resource']

        converted_items = []
        converted_links = None
        for item in return_list:
            converted_item = self.convert_standard(
                item, fields_extra, main_resource, request)
            converted_items.append(converted_item[main_resource])
            if converted_links is None:
                converted_links = converted_item.get('links')

        converted = self.dict_class(((main_resource, converted_items),))
        if converted_links:
            converted['links'] = converted_links
        return converted, main_resource

    def convert_link(self, name, value, field_extra, prefix, request):
        """Convert an ID or ID list to the JSON API RC1 format.

        Return is a tuple:
        * pattern - The pattern dictionary
        * link_id - The converted ID (or ID list, or None)
        """
        link = field_extra['link']
        if value is None:
            link_id = None
        elif link == 'from_many':
            link_id = [str(pk) for pk in value]
        else:
            assert link in ('self', 'from_one', 'to_one'), (
                '"%s" is an unexpected link type' % link)
            link_id = str(value)

        pattern = None
        if link != 'self':
            resource = field_extra.get('resource', name)
            attr_name = field_extra.get('name', name)
            base_url = request.build_absolute_uri('/api/v1/%s' % resource)

            pattern = self.dict_class((
                ('type', resource),
                ('href', base_url + '/{%s.%s}' % (prefix, attr_name)),
            ))
        return pattern, link_id

    def is_paginated(self, data):
        """Return True if data appears to be a paginated result."""
        return (
            hasattr(data, 'keys') and
            all([key in data for key in self.PAGINATION_KEYS]))


class JsonApiTemplateHTMLRenderer(TemplateHTMLRenderer):
    """Render to a template, but use JSON API format as context."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Generate JSON API representation, as well as collection."""
        # Set the context to the JSON API represention
        json_api_renderer = JsonApiRC1Renderer()
        json_api = json_api_renderer.render(
            data, accepted_media_type, renderer_context)
        context = loads(
            json_api.decode('utf-8'), object_pairs_hook=OrderedDict)

        # Is it an error?
        if 'errors' in context:
            error_context = Context(context)
            return super(JsonApiTemplateHTMLRenderer, self).render(
                error_context, accepted_media_type, renderer_context)

        # Copy main item to generic 'data' key
        other_keys = ('linked', 'links', 'meta')
        main_keys = [m for m in context.keys() if m not in other_keys]
        assert len(main_keys) == 1, (
            'Expecting one resource key, found "%s"' % main_keys)
        main_type = main_keys[0]
        main_obj = context[main_type].copy()
        main_id = main_obj['id']
        context['data'] = main_obj
        context['data']['type'] = main_type

        # Add a collection of types and IDs
        collection = {}
        for resource_type, resources in context.get('linked', {}).items():
            assert resource_type not in collection, (
                '"%s" was already added to the collection.' % resource_type)
            collection[resource_type] = {}
            for resource in resources:
                resource_id = resource['id']
                assert resource_id not in collection[resource_type], (
                    'For resource %s, ID %s is already present.'
                    % (resource_type, resource_id))
                collection[resource_type][resource_id] = resource
        collection.setdefault(main_type, {})[main_id] = main_obj
        context['collection'] = collection

        # Add language
        request = renderer_context['request']
        lang = request.GET.get('lang', translation.get_language())
        context['lang'] = lang

        # Render HTML template w/ context
        return super(JsonApiTemplateHTMLRenderer, self).render(
            context, accepted_media_type, renderer_context)

    def resolve_context(self, data, request, response):
        """Resolve context without a RequestContext."""
        if response.exception:  # pragma: no cover
            data['status_code'] = response.status_code
        return data


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
