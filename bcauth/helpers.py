"""Helper functions for Jinja2 templates"""

from allauth.account.utils import user_display
from allauth.socialaccount import providers
from allauth.socialaccount.templatetags.socialaccount import \
    get_social_accounts, get_providers

from jinja2 import contextfunction


@contextfunction
def providers_media_js(context):
    """Get a list of socialaccount providers.

    Jingo version of providers_media_js from
    allauth/socialaccount/templatetags/socialaccount.py
    """
    request = context['request']
    ret = '\n'.join(
        [p.media_js(request) for p in providers.registry.get_list()])
    return ret


def provider_login_url(
        request, provider_id, process, scope=None, auth_params=None,
        next=None):
    """Get the login URL for a socialaccount provider.

    Jingo version of provider_login_url from
    allauth/socialaccount/templatetags/socialaccount.py
    """
    provider = providers.registry.by_id(provider_id)
    query = {'process': process}
    if scope:
        query['scope'] = scope
    if auth_params:
        query['auth_params'] = auth_params
    if next:
        query['next'] = next
    else:
        next = request.POST.get('next') or request.GET.get('next')
        if next:
            query['next'] = next
        elif process == 'redirect':
            query['next'] = request.get_full_path()

    # get the login url and append query as url parameters
    return provider.get_login_url(request, **query)


env = {
    'globals': {
        'get_providers': get_providers,
        'get_social_accounts': get_social_accounts,
        'provider_login_url': provider_login_url,
        'providers_media_js': providers_media_js,
        'user_display': user_display,
    }
}
