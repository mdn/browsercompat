# -*- coding: utf-8 -*-

import collections
RouterDict = getattr(collections, 'OrderedDict', dict)

from rest_framework.compat import url
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView

from .viewsets import (
    BrowserViewSet, BrowserVersionViewSet,
    HistoricalBrowserViewSet, HistoricalBrowserVersionViewSet,
    UserViewSet)


class GroupedRouter(DefaultRouter):
    '''Router with grouped API root and slash redirects'''

    view_groups = {}

    def register(self, prefix, viewset, base_name=None, group=None):
        assert group
        self.view_groups[prefix] = group
        super(GroupedRouter, self).register(prefix, viewset, base_name)

    def get_api_root_view(self):
        """
        Return a view to use as the API root.
        """
        api_root_dict = RouterDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            group = self.view_groups[prefix]
            api_root_dict.setdefault(group, RouterDict())[prefix] = (
                list_name.format(basename=basename))

        class APIRoot(APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = RouterDict()
                for group_name, group in api_root_dict.items():
                    ret[group_name] = RouterDict()
                    for key, url_name in group.items():
                        ret[group_name][key] = reverse(
                            url_name, request=request, format=format)
                return Response(ret)

        return APIRoot.as_view()

    def get_urls(self):
        """
        Generate the list of URL patterns, including a default root view
        for the API, and appending `.json` style format suffixes.
        """
        urls = []
        assert self.include_root_view
        assert self.include_format_suffixes
        root_url = url(
            r'^$', self.get_api_root_view(), name=self.root_view_name)
        urls.append(root_url)

        default_urls = super(DefaultRouter, self).get_urls()
        urls.extend(default_urls)
        urls = format_suffix_patterns(urls)
        return urls


router = GroupedRouter(trailing_slash=False)
router.register(r'browsers', BrowserViewSet, group='resources')
router.register(r'browser-versions', BrowserVersionViewSet, group='resources')
router.register(r'users', UserViewSet, group='change-control')
router.register(
    r'historical-browsers', HistoricalBrowserViewSet, group='history')
router.register(
    r'historical-browser-versions', HistoricalBrowserVersionViewSet,
    group='history')
