# -*- coding: utf-8 -*-
"""URL router for API endpoints."""

from collections import OrderedDict

from django.conf.urls import url
from django.core.urlresolvers import RegexURLResolver
from django.views.generic import RedirectView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
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

        Include a default root view for the API, and appending `.json` style
        format suffixes.
        """
        urls = []
        assert self.include_root_view
        assert self.include_format_suffixes
        root_url = url(
            r'^$', self.get_api_root_view(), name=self.root_view_name)
        urls.append(root_url)

        default_urls = super(DefaultRouter, self).get_urls()
        urls.extend(default_urls)

        # Add format suffix versions
        # Include special-case of view_features allowing .html as well
        furls = format_suffix_patterns(urls, allowed=self.allowed_ext)
        urls = []
        for u in furls:
            assert not isinstance(u, RegexURLResolver)
            match = (
                u.name == 'viewfeatures-detail' and
                'api|json' in u.regex.pattern)
            if match:
                pattern = u.regex.pattern.replace('api|json', 'api|json|html')
                view = u._callback or u._callback_str
                u = url(pattern, view, u.default_args, u.name)
            urls.append(u)

        # Add redirects for list views
        assert not self.trailing_slash
        redirect_urls = []
        for u in default_urls:
            if u.name.endswith('-list'):
                pattern = u.regex.pattern.replace('$', '/$')
                view = RedirectView.as_view(
                    pattern_name=u.name, permanent=False, query_string=True)
                redirect_urls.append(url(pattern, view))
        return urls + redirect_urls
