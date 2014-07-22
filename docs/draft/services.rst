Services
========

A **Service** provides server functionality beyond basic manipulation of
resources.

Authentication
--------------

Several endpoint handle user authentication.

https://api.compat.mozilla.org/auth is an HTML page that shows the user's
current authentication status, and includes a button for starting a Persona_
login.

One endpoint implements Persona logins.  See the `Persona Quick Setup`_ for
details:

* ``/auth/persona/login`` - Exchanges a Persona assertion for a login cookie.
  If the email is not on the system, then a new user_ resource is created.  If
  the user has not accepted the latest version of the contribution agreement,
  then they are redirected to a page to accept it.  Otherwise, they are
  redirected to /auth.

Four endpoints are used for OAuth2_ used to exchange Persona credentials for
credentials usable from a server:

* ``/auth/oauth2/authorize``
* ``/auth/oauth2/authorize/confirm``
* ``/auth/oauth2/redirect``
* ``/auth/oauth2/access_token``

A final endpoint is used to delete the credential and log out the user:

* ``/auth/logout``

Browser Identification
----------------------

The ``/browser-ident`` endpoint provides browser identification based on the
User Agent and other parameters.

Two potential sources for this information:

* WhichBrowser_ - Very detailed.  Uses User Agent header and feature detection
  to distinguish between similar browsers.  Written in PHP.
* ua-parser_  - Parses the User Agent.  The `reference parser`_ for
  WebPlatform.org_. Written in Python.

This endpoint will probably require the browser to visit it.  It will be
further speced as part of the UX around user contributions.

.. _user: change-control.html#users

.. _OAuth2: http://tools.ietf.org/html/rfc6749
.. _Persona: http://www.mozilla.org/en-US/persona/
.. _`Persona Quick Setup`: https://developer.mozilla.org/en-US/Persona/Quick_Setup
.. _WhichBrowser: https://github.com/NielsLeenheer/WhichBrowser
.. _ua-parser: https://github.com/tobie/ua-parser
.. _`reference parser`: https://webplatform.github.io/browser-compat-model/#reference-user-agent-parser
.. _`WebPlatform.org`: http://www.webplatform.org
