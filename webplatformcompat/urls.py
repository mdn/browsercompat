from django.conf.urls import include, patterns, url
from django.views.generic.base import RedirectView
from webplatformcompat.routers import router

from .views import RequestView


webplatformcompat_urlpatterns = patterns(
    '',
    url(r'^$', RequestView.as_view(
        template_name='webplatformcompat/home.jinja2'),
        name='home'),
    url(r'^browse/', RequestView.as_view(
        template_name='webplatformcompat/browse.jinja2'),
        name='browse'),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^api/$', RedirectView.as_view(url='/api/v1/', permanent=False)),
    url(r'^api/v1/', include(router.urls)),
)
