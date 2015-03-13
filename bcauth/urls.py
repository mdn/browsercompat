"""URLs for bcauth."""
from django.conf.urls import patterns, url

bcauth_urlpatterns = patterns(
    'bcauth.views',
    url(r'^accounts/$', 'account', name='account_base'),
    url(r'^accounts/profile/$', 'profile', name='account_profile'),
)
