# -*- coding: utf-8 -*-
"""Renderer for JSON API v1.0."""

from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_client_error, is_server_error

from ..renderers import BaseJsonApiTemplateHTMLRenderer


class JsonApiV10Renderer(JSONRenderer):
    """JSON API v1.0 renderer.

    This is a partial implementation, focused on the current needs of the API.
    For the full spec, see http://jsonapi.org/format/1.0/
    """

    PAGINATION_KEYS = ('count', 'next', 'previous', 'results')
    dict_class = OrderedDict
    media_type = 'application/vnd.api+json'
    namespace = 'v2'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Convert DRF native data to the JSON API v1.0 format."""
        # Construct absolute URI for override path or request path (default)
        response = renderer_context.get('response')
        self.request = renderer_context['request']
        self.request_uri = self.request.build_absolute_uri()
        override_path = renderer_context.get('override_path')
        resource_uri = self.request.build_absolute_uri(override_path)
        fields_extra = renderer_context.get('fields_extra')
        status_code = response and response.status_code
        exception = response and getattr(response, 'exc', None)
        is_err = is_client_error(status_code) or is_server_error(status_code)
        as_relationship = renderer_context.get('as_relationship')

        if data is None:
            # Deleted items
            converted = None
        elif all([key in data for key in self.PAGINATION_KEYS]):
            # Paginated object
            converted = self.convert_paginated(
                data, fields_extra, request_uri=self.request_uri)
        elif is_err:
            converted = self.convert_error(
                data, exception, fields_extra, status_code)
        elif self.request.method == 'OPTIONS':
            converted = {'meta': data}
        elif as_relationship:
            relationship_name = as_relationship
            if as_relationship not in data:
                # Relationship to current resource in a historical viewset
                # For example, historicalbrowsers/5/relationships/browser
                # In this case, 'as_relationship' is the singular name
                # (browser), but the link ID is in 'object_id'.
                assert 'object_id' in data, (
                    'Expecting "%s" or object_id in data keys %s.'
                    % (as_relationship, list(data.keys())))
                assert 'object_id' in fields_extra, (
                    'Expecting "object_id" in fields_extra.')
                assert 'name' in fields_extra['object_id'], (
                    'Expecting "name" in fields_extra["object_id"].')
                object_name = fields_extra['object_id']['name']
                assert object_name == as_relationship, (
                    ('Expecting fields_extra["object_id"]["name"] == "%s",'
                     ' got "%s".') % (as_relationship, object_name))
                relationship_name = 'object_id'
            converted = self.convert_to_relationship_object(
                relationship_name, data[relationship_name],
                fields_extra[relationship_name],
                resource_uri=resource_uri)
        else:
            converted = self.convert_document(
                data, fields_extra, resource_uri=resource_uri,
                request_uri=self.request_uri)

        renderer_context['indent'] = 4
        return super(JsonApiV10Renderer, self).render(
            data=converted,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context)

    def convert_to_relationship_object(
            self, name, raw_id, field_data, resource_uri, include_links=True):
        """Convert from IDs to a relationship object.

        Partially implements the full spec at:
        http://jsonapi.org/format/#document-resource-object-relationships

        Expecting raw_id to be one of:
        - None (an empty to-one link)
        - A single ID (a to-one link)
        - An empty array (an empty to-many link)
        - An array of one or more IDs (a to-many link)
        The format of raw_id should agree with field_data['link']

        Return is a relationship object, such as this (include_links=True):
        {
            "data": {
                "type": "features",
                "id": "1",
            },
            "links": {
                "self": "/api/v2/features/3/relationships/parent",
                "related": "/api/v2/features/3/parent",
            },
        }
        """
        relationship = self.dict_class()
        if include_links:
            # TODO: Use reverse instead of concat to construct links
            attr_name = field_data.get('name', name)
            endpoint = field_data.get('singular', attr_name)
            scheme, netloc, path, params, query, fragment = urlparse(
                resource_uri)
            base_uri = urlunparse((scheme, netloc, path, '', '', ''))
            relationship['links'] = self.dict_class((
                ('self', base_uri + '/relationships/' + endpoint),
                ('related', base_uri + '/' + endpoint),
            ))

        link = field_data['link']
        resource = field_data.get('resource', name)
        if link in ('from_many', 'to_many'):
            data = [
                self.dict_class((('type', resource), ('id', force_text(pk))))
                for pk in raw_id]
        elif raw_id is None:
            data = None
        else:
            data = self.dict_class(
                (('type', resource), ('id', force_text(raw_id))))
        relationship['data'] = data
        return relationship

    def construct_resource_uri(self, resource_type, resource_id, field_data):
        singular = field_data.get('singular', resource_type[:-1])
        pattern = '%s:%s-detail' % (self.namespace, singular.replace('_', ''))
        url = reverse(pattern, kwargs={'pk': resource_id})
        uri = self.request.build_absolute_uri(url)
        return uri

    def convert_document(
            self, data, fields_extra, resource_uri=None, request_uri=None,
            include_relationship_links=True):
        """Convert DRF data into a JSON API document.

        Keyword Arguments:
        data - dictionary of names to DRF native values
        fields_extra - dictionary of field names to metadata
        resource_uri - the full URI of this resource, or None to derive from
            ID field and metadata
        request_uri - the full URI of the request, or None to copy the
            resource_uri
        include_relationship_links - For relationships, include or omit the
            links object
        """
        # Parse the ID data
        raw_data_id = data['id']
        id_extra = fields_extra['id']
        data_resource = id_extra['resource']
        if raw_data_id is None:
            data_id = None
        else:
            data_id = force_text(raw_data_id)
        if not resource_uri and data_id is not None:
            resource_uri = self.construct_resource_uri(
                data_resource, data_id, id_extra)
        links = self.dict_class()
        if request_uri:
            links['self'] = request_uri
        else:
            links['self'] = resource_uri

        # Parse the remaining elements
        relationships = self.dict_class()
        attributes = self.dict_class()
        view_extra = {}
        for name, value in data.items():
            field_extra = fields_extra.get(name, {})
            link = field_extra.get('link')
            is_archive_of = field_extra.get('is_archive_of')
            attr_name = field_extra.get('name', name)
            if name == 'id':
                pass  # Handled above
            elif link:
                relationship = self.convert_to_relationship_object(
                    name, value, field_extra,
                    resource_uri, include_links=include_relationship_links)
                relationships[attr_name] = relationship
            elif is_archive_of:
                archive_data = self.convert_archive_object(
                    name, value, is_archive_of)
                attributes['archive_data'] = archive_data
            elif name == '_view_extra':
                view_extra = self.convert_extra(value, field_extra)
            else:
                attributes[attr_name] = value

        # Assemble the document
        if data_resource and data_id:
            out_data = self.dict_class((
                ('type', data_resource),
                ('id', data_id),
            ))
            if attributes:
                out_data['attributes'] = attributes
            if relationships:
                out_data['relationships'] = relationships
        else:
            out_data = None
        document = self.dict_class((
            ('links', links),
            ('data', out_data),
        ))
        for name, value in view_extra.items():
            assert name not in document
            document[name] = value
        return document

    def convert_object(
            self, data, fields_extra, resource_uri=None, request_uri=None):
        """Convert DRF data into a JSON API document.

        Keyword Arguments:
        data - dictionary of names to DRF native values
        fields_extra - dictionary of field names to metadata
        resource_uri - the full URI of this resource, or None to derive from
            ID field and metadata
        request_uri - the full URI of the request, or None to copy the
            resource_uri
        """
        document = self.convert_document(
            data, fields_extra, resource_uri=resource_uri,
            request_uri=request_uri, include_relationship_links=False)
        obj = document['data']
        obj.setdefault(
            'links', self.dict_class()).update(document['links'])
        return obj

    def convert_archive_object(self, name, data, serializer):
        data.update(data.pop('links', {}))
        archive_extra = serializer.get_fields_extra()
        archive_data = self.convert_object(data, archive_extra)
        return archive_data

    def convert_error(self, data, exception, fields_extra, status_code):
        error_list = []
        errors = []
        for name, value in data.items():
            field_extra = fields_extra.get(name, {})
            is_link = bool(field_extra.get('link'))
            group = 'relationships' if is_link else 'attributes'
            parameter = getattr(exception, 'parameter', None)
            if name == 'detail':
                fmt_error = self.dict_class((
                    ('detail', value),
                    ('status', str(status_code)),
                ))
                if parameter is not None:
                    fmt_error['source'] = self.dict_class((
                        ('parameter', parameter),
                    ))
                errors.append(fmt_error)
            elif name == '_view_extra':
                for rname, error_dict in value.items():
                    assert rname != 'meta'
                    for seq, seq_errors in error_dict.items():
                        if seq is None:
                            # TODO: diagnose how subject feature errors are
                            # getting into view_extra.
                            seq = 'subject'
                        for fieldname, error_list in seq_errors.items():
                            path = '/included.%s.%s.%s' % (
                                rname, seq, fieldname)
                            assert isinstance(error_list, list)
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
                        ('path', '/data/%s/%s' % (group, name)),
                    ))
                    errors.append(fmt_error)
        assert errors, data
        return self.dict_class((('errors', errors),))

    def convert_paginated(self, data, fields_extra, request_uri):
        item_list = []
        for item in data['results']:
            converted = self.convert_object(item, fields_extra)
            item_list.append(converted)

        return self.dict_class((
            ('links', self.dict_class((
                ('self', request_uri),
                ('next', data.get('next', None)),
                ('prev', data.get('previous', None)),
            ))),
            ('data', item_list),
            ('meta', self.dict_class((
                ('count', data['count']),
            ))),
        ))

    def convert_extra(self, data, field_extra):
        extra = self.dict_class()
        for resource_name, resource_value in data.items():
            if resource_name == 'meta':
                extra['meta'] = resource_value
            else:
                serializer = resource_value.serializer.child
                fields_extra = serializer.get_fields_extra()
                for raw_resource in resource_value:
                    resource = self.convert_object(raw_resource, fields_extra)
                    extra.setdefault('included', []).append(resource)
        return extra


class JsonApiV10TemplateHTMLRenderer(BaseJsonApiTemplateHTMLRenderer):
    """Render to a template, but use JSON API format as context."""

    json_api_renderer_class = JsonApiV10Renderer

    def customize_context(self, context):
        # Add a collection of types and IDs
        collection = {}
        for resource in context.get('included', []):
            resource_id = resource['id']
            resource_type = resource['type']
            collection.setdefault(resource_type, {})[resource_id] = resource
        main_id = context['data']['id']
        main_type = context['data']['type']
        collection.setdefault(main_type, {})[main_id] = context['data']
        context['collection'] = collection
