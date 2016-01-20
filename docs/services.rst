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
  clicked or a trusted linked account says it is verified), and one is the
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

.. _user: change-control.html#users
.. _`Firefox Accounts`: https://accounts.firefox.com/signup

Data Browser
------------

The Data Browser at https://browsercompat.herokuapp.com/browse/ is an
Ember.js_ single-page app that allows browsing the resources currently
available in the API.  It is built with Ember libraries that work with
JSON API RC1.

.. _Ember.js: http://emberjs.com


Importer
--------

The MDN Importer at https://browsercompat.herokuapp.com/importer/ is used
to scrape data from MDN, extract compatibility data, pinpoint data issues on
MDN pages, and commit extracted data to the API.
