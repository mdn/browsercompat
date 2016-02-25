# -*- coding: utf-8 -*-
"""URL router for API endpoints."""

from collections import OrderedDict

from django.conf.urls import url
from django.views.generic import RedirectView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView


class GroupedRouter(DefaultRouter):
    """Router with grouped API root and slash redirects."""

    view_groups = {}
    allowed_ext = ['api', 'json']
    alt_lookup_format = '(?P<{lookup_url_kwarg}>{lookup_value})'

    def __init__(self, version, *args, **kwargs):
        self.version = version
        super(GroupedRouter, self).__init__(*args, **kwargs)

    def register(self, prefix, viewset, base_name=None, group=None):
        assert group
        self.view_groups[prefix] = group
        super(GroupedRouter, self).register(prefix, viewset, base_name)

    def get_api_root_view(self):
        """Return a view to use as the API root."""
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            group = self.view_groups[prefix]
            api_root_dict.setdefault(group, OrderedDict())[prefix] = (
                list_name.format(basename=basename))

        class APIRoot(APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = OrderedDict()
                for group_name, group in api_root_dict.items():
                    ret[group_name] = OrderedDict()
                    for key, url_name in group.items():
                        ret[group_name][key] = reverse(
                            url_name, request=request, format=format)
                return Response(ret)

        return APIRoot.as_view()

    def get_urls(self):
        """
        Return the URL patterns handled by this router.

        Same as rest_framework.routers.BaseRouter.get_urls, but
        - Adds a 'root' view for the API
        - Asserts each viewset has mapped routes
        - Adds redirects from URLs ending in slashes
        - Adds format suffix ('.json') versions
        - Adds alternate lookup views
        """
        urls = []
        assert self.include_root_view
        assert self.include_format_suffixes
        assert not self.trailing_slash
        root_url = url(
            r'^$', self.get_api_root_view(), name=self.root_view_name)
        urls.append(root_url)

        # Add URLs from registry
        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:
                # Get valid routes for the viewset, or fail
                mapping = self.get_method_map(viewset, route.mapping)
                assert mapping, 'viewset %s has no routes.' % viewset

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )
                # Add standard endpoint
                name = route.name.format(basename=basename)
                view = viewset.as_view(mapping, **route.initkwargs)
                urls.append(url(regex, view, name=name))

                # Add redirects to remove slashes
                no_slash_pattern = regex.replace('$', '/$')
                pattern_name = '%s:%s' % (self.version, name)
                view = RedirectView.as_view(
                    pattern_name=pattern_name, permanent=True,
                    query_string=True)
                urls.append(url(no_slash_pattern, view))

                # Add endpoints that include the format as an extension
                fmt_name = name
                fmt_suffixes = '|'.join(
                    getattr(viewset, 'format_suffixes', ('api', 'json')))
                fmt_regex_suffix = (
                    r'\.(?P<format>({}))/?$'.format(fmt_suffixes))
                fmt_base_pattern = regex.rstrip('$')
                fmt_regex = fmt_base_pattern + fmt_regex_suffix
                fmt_view = viewset.as_view(mapping, **route.initkwargs)
                urls.append(url(fmt_regex, fmt_view, name=fmt_name))

                # Add optional alternate lookup endpoint
                is_detail = name.endswith('detail')
                if is_detail and hasattr(viewset, 'alternate_lookup'):
                    alt_lookup_field = (
                        getattr(viewset, 'alt_lookup_field', None) or
                        'altkey')
                    alt_lookup_value_regex = (
                        getattr(viewset, 'alt_lookup_value_regex', None) or
                        '[^/.]+')
                    alt_lookup = self.alt_lookup_format.format(
                        lookup_url_kwarg=alt_lookup_field,
                        lookup_value=alt_lookup_value_regex)
                    alt_regex = route.url.format(
                        prefix=prefix,
                        lookup=alt_lookup,
                        trailing_slash='/?')
                    alt_name = '%s-by-%s' % (basename, alt_lookup_field)
                    alt_view = viewset.as_view(
                        {'get': 'alternate_lookup'}, **route.initkwargs)
                    urls.append(url(alt_regex, alt_view, name=alt_name))

                    alt_base_pattern = alt_regex.rstrip('/?$')
                    alt_fmt_regex = alt_base_pattern + fmt_regex_suffix
                    alt_fmt_view = viewset.as_view(
                        {'get': 'alternate_lookup'}, **route.initkwargs)
                    urls.append(
                        url(alt_fmt_regex, alt_fmt_view, name=alt_name))

        return urls
