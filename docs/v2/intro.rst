v2 BrowserCompat API
====================

.. Note:: This project has been cancelled, and this information is historical.

The v2 BrowserCompat API is designed to store and maintain information about
web technologies, such as HTML and CSS, in the manner used on MDN_.  This takes
the form of **Specification** tables, which detail the specifications for
technologies, and **Browser Compatibility** tables, which detail when browsers
implemented those technologies. A simple example is for the `HTML element
\<address\>`_.  A more complex example is the `CSS property display`_.

The v2 API was initially released in January 2016, and is based on
`JSON API v1.0`_. The v2 API does not implement the entire JSON API v1.0
specification. See the `issues page`_ for the list of known differences between
the v2 API and JSON API v1.0.

The v2 API is the recommended API for new code. The v1 API will be retained
until MDN tools are updated to work with the v2 API API, and then the v1 API
will be removed.

.. toctree::
   :maxdepth: 4

   implementation
   resources
   views

.. _MDN: http://developer.mozilla.org
.. _`HTML element \<address\>`: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address#Browser_compatibility
.. _`CSS property display`: https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility
.. _`JSON API v1.0`: https://jsonapi.org/format/1.0/
.. _`issues page`: ../issues.html

