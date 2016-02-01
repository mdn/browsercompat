# -*- coding: utf-8 -*-
"""Parser for JSON API RC1."""

from rest_framework.exceptions import ParseError

from ..parsers import JSONParser


class JsonApiRC1Parser(JSONParser):
    media_type = 'application/vnd.api+json'

    def parse(self, stream, media_type=None, parser_context=None):
        """Parse JSON API representation into DRF native format."""
        data = super(JsonApiRC1Parser, self).parse(
            stream, media_type=media_type, parser_context=parser_context)

        view = parser_context['view']
        model = view.queryset.model
        resource_type = model._meta.verbose_name_plural

        resource = self.dict_class()
        view_extra = self.dict_class()
        for name, value in data.items():
            if name == resource_type:
                resource = self.convert(value)
            elif name == 'linked':
                for linked_name, linked_values in value.items():
                    if linked_name == 'meta':
                        raise ParseError('"meta" not allowed in linked.')
                    view_extra[linked_name] = self.convert(linked_values)
            elif name == 'meta':
                view_extra['meta'] = value
            # JSON API requires ignoring additional attributes
        if view_extra:
            resource['_view_extra'] = view_extra
        return resource

    def convert(self, raw_data):
        if isinstance(raw_data, list):
            return [self.convert_item(item) for item in raw_data]
        else:
            return self.convert_item(raw_data)

    def convert_item(self, raw_data):
        resource = self.dict_class()
        for name, value in raw_data.items():
            if name == 'links':
                for link_name, link_value in value.items():
                    if link_name in resource:
                        raise ParseError(
                            'Attribute "%s" duplicated in links.' % link_name)
                    elif link_name == '_view_extra':
                        raise ParseError(
                            '"_view_extra" not allowed as link name.')
                    resource[link_name] = link_value
            elif name == '_view_extra':
                raise ParseError(
                    '"_view_extra" not allowed as attribute name.')
            else:
                if name in resource:
                    raise ParseError(
                        'Link %s duplicated in attributes.' % name)
                resource[name] = value
        return resource
