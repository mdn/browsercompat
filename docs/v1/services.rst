Services
========

A **Service** provides server functionality beyond basic manipulation of
resources.

Authentication
--------------

Several endpoint handle user authentication.

https://browsersupports.org/accounts/profile/ is an HTML page that summarizes the
users' account, which includes:

* The username, which can't be changed.
* Changing or setting the password, which is optional if a linked account is
  used.
* Viewing, adding, and removing linked accounts, which are optional if a
  password is set.  The support linked account type is `Firefox Accounts`_.
* Viewing, adding, and removing emails.  Emails can be verified (a link is
  clicked or a trusted linked accout says it is verified), and one is the
  primary email used for communication.

Additional endpoints for authentication:

* ``/accounts/`` - Redirect to login or profile, depending on login state
* ``/accounts/signup/`` - Create a new account, using username and password
* ``/accounts/login/`` - Login to an existing account, using username and
  password or selecting a linked account
* ``/accounts/logout/`` - Logout from site
* ``/accounts/password/change/`` - Change an existing password
* ``/accounts/password/set/`` - Set the password for an account using only a
  linked account
* ``/accounts/email/`` - Manage associated email addresses
* ``/accounts/password/reset/`` - Start a password reset via email
* ``/accounts/social/connections/`` - Manage social accounts
* ``/accounts/fxa/login/`` - Start a `Firefox Accounts`_ login


Browser Identification
----------------------

The ``/browser_ident`` endpoint provides browser identification based on the
User Agent and other parameters.

Two potential sources for this information:

* WhichBrowser_ - Very detailed.  Uses User Agent header and feature detection
  to distinguish between similar browsers.  Written in PHP.
* ua-parser_  - Parses the User Agent.  The `reference parser`_ for
  WebPlatform.org_. Written in Python.

This endpoint will probably require the browser to visit it.  It will be
further speced as part of the UX around user contributions.

.. _user: change-control.html#users

.. _`Firefox Accounts`: https://accounts.firefox.com/signup
.. _WhichBrowser: https://github.com/NielsLeenheer/WhichBrowser
.. _ua-parser: https://github.com/tobie/ua-parser
.. _`reference parser`: https://webplatform.github.io/browser-compat-model/#reference-user-agent-parser
.. _`WebPlatform.org`: http://www.webplatform.org
