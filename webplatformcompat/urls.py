from django.conf.urls import patterns, url

from .views import RequestView

webplatformcompat_urlpatterns = patterns(
    '',
    url('^$', RequestView.as_view(
        template_name='webplatformcompat/home.jinja2'),
        name='home'),
)
