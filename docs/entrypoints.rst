Entrypoints
-----------

A developer-centered website is available at
https://browserscompat.herokuapp.com/.  This site includes

* `/api/v1`_ - The legacy v1 API, conforming to the deprecated `JSON API`_ RC1
  specification.
* `/api/v2`_ - The current v2 API, conforming to the `JSON API v1.0`_
  specification.
* `/browse`_ - A data browser.
* `/importer`_ - A tool for scraping and validating data from MDN_.

The APIs support two representations:

``application/vnd.api+json`` *(default)*
  JSON in the JSON API format.
``text/html``
  The Django REST Framework browsable API.

The API supports user accounts with password and/or Persona_ authentication.


.. _`Django REST Framework browsable API`: http://www.django-rest-framework.org/topics/browsable-api
.. _Persona: http://www.mozilla.org/en-US/persona/
.. _`/api/v1`:  https://browsercompat.herokuapp.com/api/v1
.. _`JSON API`: http://jsonapi.org
.. _`/api/v2`:  https://browsercompat.herokuapp.com/api/v2
.. _`JSON API v1.0`: http://jsonapi.org/format/1.0/
.. _`/browse`: https://browsercompat.herokuapp.com/browse
.. _`/importer`: https://browsercompat.herokuapp.com/importer
.. _MDN: https://developer.mozilla.org
