v1 BrowserCompat API
====================

.. Note:: This project has been cancelled, and this information is historical.

The v1 API was designed to store and maintain information about web technologies,
such as HTML and CSS, in the manner used on MDN_.  This takes the form of
**Specification** tables, which detail the specifications for technologies,
and **Browser Compatibility** tables, which detail when browsers implemented
those technologies. A simple example is for the `HTML element \<address\>`_.
A more complex example is the `CSS property display`_.

The v1 API was designed in March 2014, and implemented over the next year.
It was allowed to be partially implemented, and labeled as "draft", so that
the design could be modified as new problems were discovered. The API as
designed is mostly implemented as of December 2015, but further changes will
be made to the v1 API in 2016. See the `issues page`_ for details.

The v1 API was based on release candidate 1 (RC1) of the `JSON API`_
specification, which was released 2014-07-05.  Starting with RC2 on 2015-02-18,
The JSON API team rapidly iterated on the design, making significant changes
informed by the experience of implementors.  `JSON API v1.0`_ was
released May 2015, and is significantly different from RC1.  The JSON API team
does not preserve documentation for release candidates (online or with
a git tag), so it is impossible to refer to the documentation for RC1.

v1 will remain on JSON API RC1. The next version of the API, v2, will support
JSON API 1.0.  Both the v1 and v2 APIs will be supported until the tools are
updated, and then the v1 API will be retired.

.. toctree::
   :maxdepth: 4

   resources
   change-control
   history
   views

.. _MDN: http://developer.mozilla.org
.. _`HTML element \<address\>`: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address#Browser_compatibility
.. _`CSS property display`: https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility
.. _`JSON API`: https://jsonapi.org/
.. _`JSON API v1.0`: https://jsonapi.org/format/1.0/
.. _`issues page`: ../issues.html

