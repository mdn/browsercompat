Entrypoints
-----------

The v1 API can be found at https://browsercompat.herokuapp.com/api/v1/.
It includes a browsable API to ease application development.

The API supports two representations:

``application/vnd.api+json`` *(default)*
  JSON mostly conforming to the `JSON API`_ RC1 specification.
``text/html``
  the Django REST Framework browsable API.

The API supports user accounts with Persona_ authentication.

A developer-centered website is available at
https://browserscompat.herokuapp.com/.  This site includes a `data browser`_
and an importer_ for scraping data from MDN_.

.. _`JSON API`: http://jsonapi.org
.. _`Django REST Framework browsable API`: http://www.django-rest-framework.org/topics/browsable-api
.. _Persona: http://www.mozilla.org/en-US/persona/
.. _`data browser`: https://browsercompat.herokuapp.com/browse
.. _importer: https://browsercompat.herokuapp.com/importer
.. _MDN: https://developer.mozilla.org
