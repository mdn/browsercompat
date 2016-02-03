"""Main URL configuration for website."""
from django.conf.urls import patterns, include, url
from django.contrib import admin

from bcauth.urls import bcauth_urlpatterns
from bcauth.oauth2p import urls as oauth2_provider_urls
from webplatformcompat.urls import webplatformcompat_urlpatterns

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(bcauth_urlpatterns)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'', include(webplatformcompat_urlpatterns)),
    url(r'^oauth2/', include(
        oauth2_provider_urls, namespace='oauth2_provider')),
)
