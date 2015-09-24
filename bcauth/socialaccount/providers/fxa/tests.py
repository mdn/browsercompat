"""Tests for FirefoxAccounts.

Uses the testing infrastructure from django-allauth.
"""

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry
from django.core.urlresolvers import reverse


from .provider import FirefoxAccountsProvider

# Setup base class but omit from nose tests
create_oauth2_tests.__test__ = False
base_class = create_oauth2_tests(
    registry.by_id(FirefoxAccountsProvider.id))
base_class.__test__ = False


class FirefoxAccountsTest(base_class):
    __test__ = True  # Include in nose tests

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "uid":"6d940dd41e636cc156074109b8092f96",
            "email":"user@example.domain"
        }""")

    def test_authentication_error(self):
        """Test authentication errors.

        Because we're using a jinja2 template, assertTemplateUsed does not
        work.  See https://code.djangoproject.com/ticket/24622.
        """
        resp = self.client.get(reverse(self.provider.id + '_callback'))
        self.assertContains(
            resp, "<title>Social Network Login Failure</title>", html=True)
