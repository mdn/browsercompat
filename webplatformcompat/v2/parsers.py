# -*- coding: utf-8 -*-
"""Parser for JSON API v1.0."""

from rest_framework.exceptions import ParseError

from ..parsers import JSONParser


class JsonApiV10Parser(JSONParser):
    """JSON API v1.0 parser.

    This is a partial implementation, focused on the current needs of the API.
    For the full spec, see http://jsonapi.org/format/1.0/
    """

    media_type = 'application/vnd.api+json'

    def parse(self, stream, media_type=None, parser_context=None):
        """Parse JSON API representation into DRF native format."""
        data = super(JsonApiV10Parser, self).parse(
            stream, media_type=media_type, parser_context=parser_context)
        fields_extra = parser_context.get('fields_extra', {})
        as_relationship = parser_context.get('as_relationship')

        if as_relationship:
            # If the key is not found, it's a programmer error
            rel_field_data = fields_extra[as_relationship]
            expected_type = rel_field_data.get('resource', as_relationship)
            rel_linkage = self.convert_relationships_object(
                'data', data['data'], expected_type)
            resource = self.dict_class(((as_relationship, rel_linkage),))
        elif 'data' in data:
            main_type, resource = self.convert_resource_object(
                'data', data['data'], fields_extra, id_required=False)
        else:
            resource = self.dict_class()

        # Add extra data to _view_extra
        view_extra = self.dict_class()
        if 'meta' in data:
            view_extra['meta'] = data['meta']
        if 'included' in data:
            for seq, item in enumerate(data['included']):
                prefix = 'included.%d' % seq
                item_type, converted = self.convert_resource_object(
                    prefix, item, fields_extra, id_required=True)
                view_extra.setdefault(item_type, []).append(converted)
        if view_extra:
            resource['_view_extra'] = view_extra

        return resource

    invalid_names = ('_view_extra', 'meta', 'id')

    def convert_relationships_object(
            self, prefix, raw_data, expected_type=None):
        """Convert a relationships object.

        Partially implements full spec at:
        http://jsonapi.org/format/1.0/#document-resource-object-relationships

        Keyword Arguments:
        prefix - The JSON path to this relationship object, for errors
        raw_data - The value of the relationship
        expected_type - The expected type of the resource identifiers, or None
            to skip verification.

        raw_data is expected to be a single resource identifier object:

        {'type': 'features': 'id': 1}

        or an array of resource identifier objects:

        [
            {'type': 'features': 'id': 1},
            {'type': 'features', 'id': 2},
        ]

        or None for an empty to-one relationship.

        Return is resource linkage, depending on the type of linkage:
          * None (an empty to-one link)
          * A single ID (a to-one link)
          * An empty array (an empty to-many link)
          * An array of IDs (a to-many link)
        """
        if raw_data is None:
            return None

        if isinstance(raw_data, list):
            data = raw_data
            many = True
        else:
            data = [raw_data]
            many = False

        item_ids = []
        for seq, item in enumerate(data):
            if many:
                seq_prefix = '%s.%d' % (prefix, seq)
            else:
                seq_prefix = prefix
            item_id = self.convert_resource_identifier(
                seq_prefix, item, expected_type, id_required=True)
            item_ids.append(item_id)
        if many:
            return item_ids
        else:
            return item_ids[0]

    def convert_resource_object(self, prefix, data, fields_extra, id_required):
        """Convert a resource object.

        Partially implements the spec at:
        http://jsonapi.org/format/1.0/#document-resource-objects

        Expecting something like:
        {
            'type': 'features',
            'id': '2',
            'attributes': {
                'slug': 'the_slug',
                'name': {'en': 'The Name'},
            },
            'relationships': {
                'parent': {
                    'data': {'type': 'features', 'id': '1'},
                },
                'children': {
                    'data': [
                        {'type': 'features', 'id': '3'},
                        {'type': 'features', 'id': '4'},
                    ]
                }
            }
        }

        Return is a two-element tuple:
        - The type of the resource
        - A dictionary combining the ID, attributes, and relationships
        """
        assert not isinstance(data, list), 'Arrays are not handled.'

        resource = self.dict_class()
        assert 'resource' in fields_extra['id'], (
            'The id field must define the resource.')
        resource_type = fields_extra['id']['resource']
        resource_id = self.convert_resource_identifier(
            prefix, data, resource_type, id_required)
        if resource_id is not None:
            resource['id'] = resource_id

        attributes = data.get('attributes', {})
        for name, value in attributes.items():
            if name in self.invalid_names:
                raise ParseError(
                    ('"%s" is not allowed in %s.attributes.' %
                     (name, prefix)))
            resource[name] = value

        relationships = data.get('relationships', {})
        for name, relationship in relationships.items():
            if name in self.invalid_names:
                raise ParseError(
                    ('"%s" is not allowed in %s.relationships.' %
                     (name, prefix)))
            if name in resource:
                raise ParseError(
                    ('"%s" can not be in both %s.attributes and'
                     ' %s.relationships.' % (name, prefix, prefix)))
            if 'data' not in relationship:
                raise ParseError(
                    ('"data" is required in %s.relationships.%s.' %
                     (prefix, name)))

            rel_prefix = '%s.relationships.%s.data' % (prefix, name)
            if name in fields_extra:
                rel_type = fields_extra[name].get('resource', name)
            else:
                # Don't verify the type, similar to unknown attributes
                # ParseError might cause future problems
                # Ignoring is also an option, serializer default is to ignore
                rel_type = None
            resource[name] = self.convert_relationships_object(
                rel_prefix, relationship['data'], rel_type)
        return resource_type, resource

    def convert_resource_identifier(
            self, prefix, data, expected_type=None, id_required=True):
        """Convert a single resource identifier object.

        Partially implements the spec at:
        http://jsonapi.org/format/1.0/#document-resource-identifier-objects

        Expecting data to be a resource identifier, such as:

        {'type': 'features': 'id': 1}

        Return is the resource ID, such as '1'.
        """
        try:
            resource_id = data['id']
        except KeyError:
            if id_required:
                raise ParseError('%s.id is required.' % prefix)
            else:
                resource_id = None

        try:
            resource_type = data['type']
        except KeyError:
            raise ParseError('%s.type is required.' % prefix)

        if expected_type is not None and resource_type != expected_type:
            raise ParseError(
                '%s.type should be "%s", is "%s".' %
                (prefix, expected_type, resource_type))

        return resource_id
