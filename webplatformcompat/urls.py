"""URLs for API and sample views."""
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from mdn.urls import mdn_urlpatterns
from webplatformcompat.v1.routers import router as v1_router
from webplatformcompat.v2.routers import router as v2_router

from .views import ViewFeature


webplatformcompat_urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(
        template_name='webplatformcompat/home.html'),
        name='home'),
    url(r'^about/', TemplateView.as_view(
        template_name='webplatformcompat/about.html'),
        name='about'),
    url(r'^browse/', TemplateView.as_view(
        template_name='webplatformcompat/browse.html'),
        name='browse'),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^api/$', TemplateView.as_view(
        template_name='webplatformcompat/api.html'),
        name='api'),
    url(r'^api/v1/', include(v1_router.urls, namespace='v1')),
    url(r'^api/v2/', include(v2_router.urls, namespace='v2')),
    url(r'^importer$', RedirectView.as_view(
        url='/importer/', permanent=False)),
    url(r'^importer/', include(mdn_urlpatterns)),
    url(r'^view_feature/(?P<feature_id>\d+)(.html)?$', ViewFeature.as_view(
        template_name='webplatformcompat/feature-js.html'),
        name='view_feature'),
)
