Entrypoints
-----------

The API will be reachable at https://developer.mozilla.org/compat/api. A non-SSL
version will be reachable at http://developer.mozilla.org/compat/api, and will
redirect to the SSL version.  This site is for applications that read,
create, update, and delete compatibility resources.  It includes a
browsable API to ease application development, but not full documentation.

The API supports two representations:

``application/vnd.api+json`` *(default)*
  JSON mostly conforming to the `JSON API`_.
``text/html``
  the Django REST Framework browsable API.

The API supports user accounts with Persona_ authentication.  Persona
credentials can be exchanged for an `OAuth 2.0`_ token for server-side code
changes.

A developer-centered website will be available at <https://developer.mozilla.org/compat>.
A non-SSL version will be available at <http://developer.mozilla.org/compat> and will
redirect to the HTTPS version.  This site is for documentation, example code,
and example presentations.

The documentation site is not editable from the browser.  It uses gettext-style
translations.  en-US will be the first supported language.

.. _`JSON API`: http://jsonapi.org
.. _`Django REST Framework browsable API`: http://www.django-rest-framework.org/topics/browsable-api
.. _Persona: http://www.mozilla.org/en-US/persona/
.. _`OAuth 2.0`: http://oauth.net/2/

