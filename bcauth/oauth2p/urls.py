"""
Overrides for oauth2_provider.urls.

Same as default, but uses our AuthorizationView.
"""
from __future__ import absolute_import
from django.conf.urls import url

from oauth2_provider import views
from .views import MyAuthorizationView

urlpatterns = (
    url(r'^authorize/$', MyAuthorizationView.as_view(), name='authorize'),
    url(r'^token/$', views.TokenView.as_view(), name='token'),
    url(r'^revoke_token/$', views.RevokeTokenView.as_view(),
        name='revoke-token'),
)

# Application management views
urlpatterns += (
    url(r'^applications/$', views.ApplicationList.as_view(), name='list'),
    url(r'^applications/register/$', views.ApplicationRegistration.as_view(),
        name='register'),
    url(r'^applications/(?P<pk>\d+)/$', views.ApplicationDetail.as_view(),
        name='detail'),
    url(r'^applications/(?P<pk>\d+)/delete/$',
        views.ApplicationDelete.as_view(), name='delete'),
    url(r'^applications/(?P<pk>\d+)/update/$',
        views.ApplicationUpdate.as_view(), name='update'),
)

urlpatterns += (
    url(r'^authorized_tokens/$', views.AuthorizedTokensListView.as_view(),
        name='authorized-token-list'),
    url(r'^authorized_tokens/(?P<pk>\d+)/delete/$',
        views.AuthorizedTokenDeleteView.as_view(),
        name='authorized-token-delete'),
)
