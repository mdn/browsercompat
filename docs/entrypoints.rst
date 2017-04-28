Entrypoints
-----------

.. Note:: This project has been cancelled, and this information is historical.

This entrypoints are

* ``/api/v1`` - The legacy v1 API, conforming to the deprecated `JSON API`_ RC1
  specification.
* ``/api/v2`` - The current v2 API, conforming to the `JSON API v1.0`_
  specification.
* ``/browse`` - A data browser.
* ``/importer`` - A tool for scraping and validating data from MDN_.

The APIs support two representations:

``application/vnd.api+json`` *(default)*
  JSON in the JSON API format.
``text/html``
  The Django REST Framework browsable API.

The API supports user accounts with password and/or Persona_ authentication.


.. _`Django REST Framework browsable API`: http://www.django-rest-framework.org/topics/browsable-api
.. _Persona: http://www.mozilla.org/en-US/persona/
.. _`JSON API`: http://jsonapi.org
.. _`JSON API v1.0`: http://jsonapi.org/format/1.0/
.. _MDN: https://developer.mozilla.org
