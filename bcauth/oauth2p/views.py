"""Overrides for oauth2_provider.views."""

from oauth2_provider.views.base import (
    AuthorizationView, BaseAuthorizationView)
from oauth2_provider.http import HttpResponseUriRedirect


class MyAuthorizationView(AuthorizationView):
    """Handle Authorization Requests.

    Same as oauth2_provider.views.AuthorizationView, except
    that error_response doesn't add a 'url' variable to the context,
    overriding the 'url' reverse function.
    """

    def error_response(self, error, **kwargs):
        """Handle errors with a redirect or an error response."""
        redirect, error_response = super(
            BaseAuthorizationView, self).error_response(error, **kwargs)

        if redirect:
            return HttpResponseUriRedirect(error_response['url'])

        status = error_response['error'].status_code
        error_response.pop('url', None)
        return self.render_to_response(error_response, status=status)
