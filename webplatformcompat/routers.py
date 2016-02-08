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
        """
        urls = []
        assert self.include_root_view
        assert self.include_format_suffixes
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
                view = RedirectView.as_view(
                    pattern_name=name, permanent=False, query_string=True)
                urls.append(url(no_slash_pattern, view))

                # Add endpoints that include the format as an extension
                fmt_name = name
                fmt_regex_suffix = r'\.(?P<format>(api|json))/?$'
                fmt_base_pattern = regex.rstrip('$')
                if name == 'viewfeatures-detail':
                    fmt_regex_suffix = r'\.(?P<format>(api|json|html))/?$'
                fmt_regex = fmt_base_pattern + fmt_regex_suffix
                fmt_view = viewset.as_view(mapping, **route.initkwargs)
                urls.append(url(fmt_regex, fmt_view, name=fmt_name))
        return urls
