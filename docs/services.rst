Services
========

.. Note:: This project has been cancelled, and this information is historical.

A **Service** provides server functionality beyond basic manipulation of
resources.

Authentication
--------------

Several endpoint handle user authentication.

https://browsercompat.org/accounts/profile/ is an HTML page that summarizes the
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

OAuth2 Authentication
---------------------

A user can register an OAuth2 client application, and then use that
application to provision bearer tokens on behalf of users.  `OAuth2 Simplified`
is a technical but gentle introduction to OAuth2. The
`OAuth2 website`_ is a decent starting point for learning how OAuth 2.0
works and finding some (older) client libraries, and the
`OAuth2 specification`_ has details on the protocols.

.. _`OAuth2 Simplified`: https://aaronparecki.com/2012/07/29/2/oauth2-simplified
.. _`OAuth2 website`: http://oauth.net
.. _`OAuth2 specification`: http://tools.ietf.org/html/rfc6749

Back-End Applications
~~~~~~~~~~~~~~~~~~~~~
When the application is going to run on a server or a local machine, it is
possible to keep a client secret secure, and authenticate the client to the
server using this secret.

The steps are:

1. Setup your OAuth2 Confidential Client Application
2. Request an authorization code for your user
3. Exchange the authorization code for an access token
4. Use the access token to access the API
5. Refresh the access token as needed

Setup Application
*****************

First, log into the API and go to your profile page (``/accounts/profile/``,
linked under your username in the title bar).

Next, select "Apps" from the profile menu, going to ``/oauth2/applications/``.
Select "New Application".

Fill in the form:

* Name - A descriptive name, or your website URL. This will be displayed
  to your users.
* Client ID - Keep the generated value
* Client secret - Keep the generate value
* Client type - Confidential
* Authorization grant type - Authorization code
* Redirect uris - One or more redirect URIs owned by your client application.
  This could be a localhost URI for development, and/or a URI on your
  deployed website.

Select Save.

Request Auth Code
*****************
When you need to make an authenticated request on behalf of a user, start the
process by requesting an authorization code.

Redirect the user to the authorization endpoint (broken up to show query parameters)::

    https://browsercompat.org/oauth2/authorize/?
       response_type=code&
       client_id=CLIENT_ID&
       redirect_uri=REDIRECT_URI&
       scope=read write

The user will login if they are not already logged in, and then asked if they
want to authorize your application.  If they say yes, your redirect URI will
be called with the query string ``?code=AUTHORIZATION_CODE``. If there was a
problem, including the user denying access, then the query string will be
``?error=ERROR_TYPE``. See the `Authorization Grant Error Response`_ section in
the OAuth2 spec for possible error types.

.. _`Authorization Grant Error Response`: http://tools.ietf.org/html/rfc6749#section-4.1.2.1

Exchange for Token
******************
So far, the communication has been over the internet in the user's browser.
The backend server communicates directly with the authorization server to
exchange the authorization code for an access token. The authorization code
is valid for a short time.

The backend server POST to this URL::

    https://browsercompat.org/oauth2/token/

with this form-encoded content::

    grant_type=authorization_code&
    code=AUTHORIZATION_CODE&
    redirect_uri=REDIRECT_URI&
    client_id=CLIENT_ID&
    client_secret=CLIENT_SECRET

The authorization server will response with JSON:

.. code-block:: json

    {
        "expires_in": 36000,
        "token_type": "Bearer",
        "access_token": "ACCESS_TOKEN",
        "refresh_token": "REFRESH_TOKEN",
        "scope": "read write"
    }

Access the API
**************
When accessing the API on behalf of the user, include the access token in the
``Authorization`` header:

.. code-block:: http

    POST /api/v2/supports
    Host: browsercompat.org
    Content-Type: application/vnd.api+json
    Accept: application/vnd.api+json
    Authorization: Bearer ACCESS_TOKEN

.. literalinclude:: /v2/raw/support-create-minimal-request-body.json
    :language: json

The command line tool ``curl`` can also be used. Let's say you wanted to add
a note to the support with ID 1.  If you place this JSON API request in a 
file named "update.json":

.. code-block:: json

    {
        "data": {
            "type": "supports",
            "id": "1",
            "attributes": {
                "note": {
                    "en": "Added a note"
                }
            }
        }
    }

then this ``curl`` command will update the API::

    curl -v -X PATCH
         -H "Content-Type: application/vnd.api+json" \
         -H "Accept: application/vnd.api+json" \
         -H "Authorization: Bearer ACCESS_TOKEN" \
         -d @update.json \
         https://browsercompat.org/api/v2/supports/1

Invalid Tokens
**************
The token can expire because the user revoked it (see the Token section of your
profile in the API), or because the token expired.  The access token has an
expiration date of 36000 seconds (10 hours). When you try to use an invalid
access token, you'll get an authorization denied response:

.. code-block:: http


    HTTP/1.0 401 UNAUTHORIZED
    Content-Type: application/vnd.api+json
    WWW-Authenticate: Bearer realm="api"

.. code-block:: json

    {
        "errors": [
            {
                "detail": "Authentication credentials were not provided.",
                "status": "401"
            }
        ]
    }

Refresh the Token
*****************
If a token is not revoked, you can use the refresh token to provision a new
access token. POST to the token URL again
(https://browsercompat.org/oauth2/token/), with the form data::

    grant_type=refresh_token&
    refresh_token=REFRESH_TOKEN&
    client_id=CLIENT_ID&
    client_secret=CLIENT_SECRET

The response is another access token response, with a fresh access token and
a fresh refresh token. A token can also be refreshed before the access token
expires.

Front-End or Mobile Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For a front-end application, all the code is in JavaScript, and any secret
would be included in the source code downloaded to the user's browser. Mobile
applications, such as iPhone or Android applications, use compiled code, but
any client secret would still have to be present in application code. Because
of this, OAuth can't be used directly with client secrets, and thus the client
can't authenticate itself to the server.

One way to retain authentication is to use an API proxy, where the application
talks to a thin backend that handles the details of the OAuth2 protocol. See
Alex Bilbie's post, `OAuth and Single Page JavaScript Web-Apps`_ for a
discussion of why this is a good idea, and a sketch of how to implement it.

Because the API does not expose user's information, we allow the
`Implicit Grant`_ authentication type, which does not authenticate the client,
but relies on a predetermined client URL to accept tokens after user
authentication.

The steps are:

1. Setup your OAuth2 Public Client Application
2. Request an access token for your user
3. Use the access token to access the API
4. Refresh the access token as needed

.. _`OAuth and Single Page JavaScript Web-Apps`: http://alexbilbie.com/2014/11/oauth-and-javascript/
.. _`Implicit Grant`: http://tools.ietf.org/html/rfc6749#section-4.2

Setup Application
*****************

First, log into the API and go to your profile page (``/accounts/profile/``,
linked under your username in the title bar).

Next, select "Apps" from the profile menu, going to ``/oauth2/applications/``.
Select "New Application".

Fill in the form:

* Name - A descriptive name, or your website URL. This will be displayed
  to your users.
* Client ID - Keep the generated value
* Client secret - Keep the generate value
* Client type - Public
* Authorization grant type - Implicit
* Redirect uris - One or more redirect URIs owned by your client application.
  This could be a localhost URI for development, and/or a URI on your
  deployed website.

Select Save.

Request a Token
***************
To request a access token, redirect the user to the authorization endpoint
(broken up to show query parameters)::

    https://browsercompat.org/oauth2/authorize/?
       response_type=token&
       client_id=CLIENT_ID&
       redirect_uri=REDIRECT_URI&
       scope=read write

The user will login if they are not already logged in, and then asked if they
want to authorize your application.  If they say yes, your redirect URI will
be called with a long fragment string::

    https://yoursite.com/redirect#
        expires_in=36000&
        state=&
        token_type=Bearer&
        access_token=ACCESS_TOKEN&
        scope=read+write

Your code will proceess the fragment string to extract the access token.

If there is an error, you will get a response like::

    https://yoursite.com/redirect#error=access_denied

See the `Implicit Grant Error Response`_ section in the OAuth2 spec for
possible error types.

.. _`Implicit Grant Error Response`: http://tools.ietf.org/html/rfc6749#section-4.2.2.1

Using the Token
***************

To use the access code, add an ``Authorization`` header with the value
``Bearer ACCES_TOKEN``. See `Access The API`_ in the back-end client section
for more details.

The token will eventually expire, and the API request will fail. See `Invalid
Tokens`_ in the back-end client section for details. Implicitly granted tokens
do not have an associated refresh token, and the user must return to the API to
grant access again.

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
