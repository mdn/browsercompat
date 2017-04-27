Installation
============

.. Note:: This project has been cancelled, and this information is historical.

Install Django Project
----------------------
For detailed local installation instructions, including OS-specific
instructions, see the `Installation page on the wiki`_.

1. Install system packages and libraries.  The required packages are
   Python_ (2.7, 3.4, and/or 3.5),
   pip_ (latest), and
   virtualenv_ (latest).
   To match production and for a smooth installation of Python packages,
   install
   PostgreSQL_ (9.2 or later recommended) and
   Memcached_ (latest).
   virtualenvwrapper_ and autoenv_ will make your development life easier.
2. Optionally, provision a PostgreSQL database, recommended to match
   production.  The default Django database settings will use a
   SQLite_ database named ``db.sqlite3``.
3. Optionally, run Redis_ or Memcached_ for improved read performance
   (production uses Redis for caching and for the Celery_ backend)
   The default settings will run without a cache or asynchronous tasks.
4. `Clone project locally`_.
5. `Create a virtualenv`_.
6. Install dependencies with
   ``pip install -r requirements/development.txt``.
7. Customize the configuration with environment variables.
   See ``wpcsite/settings.py`` and ``env.dist`` for advice and available
   settings.
8. Initialize the database and a superuser account with
   ``./manage.py migrate``.
9. Verify that tests pass with ``./manage.py test`` or ``make test``.
10. Run it with ``./manage.py runserver`` or ``./manage.py runserver_plus``.

.. _Installation page on the wiki: https://github.com/mdn/browsercompat/wiki/Installation
.. _Python: https://www.python.org
.. _pip: https://pip.pypa.io/en/latest/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _PostgreSQL: http://www.postgresql.org
.. _Redis: http://redis.io
.. _Memcached: http://memcached.org
.. _Celery: http://www.celeryproject.org
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/
.. _autoenv: https://github.com/kennethreitz/autoenv
.. _`Create a virtualenv`: https://virtualenv.pypa.io/en/latest/userguide.html
.. _SQLite: http://sqlite.org


Install in Heroku
-----------------

Heroku_ allows you to quickly deploy browsercompat.  Heroku hosts
the beta version of the service at https://browsercompat.herokuapp.com, using
the add-ons:

- `heroku-postgresql`_ (`hobby-basic tier`_, $9/month, required for size
  of dataset)
- `memcachier`_ (free dev tier)
- `heroku-redis`_ (free `hobby-dev tier`_)
- Mozilla's New Relic account (`Heroku New Relic`_ available, including free `Wayne tier`_)

For more details of the beta server, see `Beta Server`_ on the github wiki.


To deploy with Heroku, you'll need to `signup for a free account`_ and
install the `Heroku Toolbelt`_.   Then you can:

1. Clone project locally
2. ``heroku apps:create``
3. ``git push heroku master``
4. See the current config with ``heroku config``, and then customize with
   environment variables using ``heroku config:set``
   (see ``wpcsite/settings.py`` and ``env.dist``)
5. Add superuser account (``heroku run ./manage.py createsuperuser``)

.. _Heroku: https://www.heroku.com/
.. _`signup for a free account`: https://signup.heroku.com/
.. _`Heroku Toolbelt`: http://toolbelt.heroku.com/
.. _`heroku-postgresql`: https://devcenter.heroku.com/articles/heroku-postgresql
.. _`hobby-basic tier`: https://devcenter.heroku.com/articles/heroku-postgres-plans
.. _`memcachier`: https://devcenter.heroku.com/articles/memcachier
.. _`heroku-redis`: https://devcenter.heroku.com/articles/heroku-redis
.. _`hobby-dev tier`: https://elements.heroku.com/addons/heroku-redis
.. _`Heroku New Relic`: https://devcenter.heroku.com/articles/newrelic
.. _`Wayne tier`: https://elements.heroku.com/addons/newrelic#plan_selector
.. _`Beta Server`: https://github.com/mdn/browsercompat/wiki/Beta-Server

Configuring authentication
--------------------------
The project uses `django-allauth`_ as a framework for local and social
authentication.  The `public service`_ uses username and password for local
authentication, and `Firefox Accounts`_ (FxA) for social authentication.

django-allauth supports multiple emails per user, with one primary email
used for communication.  Email addresses are validated by sending a
confirmation link.  For a public server, you'll need to
`configure Django to send email`_, by configuring your mail server and setting
environment variables.  For local development, it is easiest to print
emails to the console::

    export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"

django-allauth supports many social authentication providers. See the
`providers documentation`_ for the current list and hints for configuration.
Using an authentication provider is not required, especially for local
development.  Instead, use local authentication with a username and password.

If you need FxA integration, see the `Firefox Accounts page on the wiki`_
for install hints.

.. _`django-allauth`: http://www.intenct.nl/projects/django-allauth/
.. _`public service`: https://browsercompat.herokuapp.com
.. _`Firefox Accounts`: https://developer.mozilla.org/en-US/Firefox_Accounts
.. _`configure Django to send email`: https://docs.djangoproject.com/en/1.7/topics/email/
.. _`providers documentation`: http://django-allauth.readthedocs.org/en/latest/providers.html
.. _`Firefox Accounts page on the wiki`: https://github.com/mdn/browsercompat/wiki/Firefox%20Accounts


Load Data
---------
There are several ways to get data into your API:

1. Load data from documentation fixtures
2. Load data from the github export
3. Load data from another browsercompat server

Load from documentation fixtures
********************************
The integration tests and documentation use a subset of real compatibility
data. This subset isn't enough for a local compatibility server, but should be
adequate for development work on the API software, and takes less than a minute
to load:

1. Run the API (``./manage.py runserver``)
2. Import the data (``tools/upload_data.py --data docs/v1/resources``)

Load from GitHub
****************
The data on browsercompat.herokuapp.com_ is archived in the
`browsercompat-data`_ github repo, and this is the fastest way to get complete
data into your empty API:

1. Clone the github repo (``git clone https://github.com/mdn/browsercompat-data.git``)
2. Run the API (``./manage.py runserver``)
3. Import the data (``tools/upload_data.py --data /path/to/browsercompat-data/data``)

Load from another browsercompat server
**************************************
If you have read access to a browsercompat server that you'd like to clone, you
can grab the data for your own server.

1. Download the data (``tools/download_data.py --api https://browsercompat.example.com``)
2. Run the API (``./manage.py runserver``)
3. Import the data (``tools/upload_data.py``)

.. _MDN: https://developer.mozilla.org/en-US/
.. _`github project`: https://github.com/webplatform/compatibility-data
.. _browsercompat.herokuapp.com: https://browsercompat.herokuapp.com
.. _`browsercompat-data`: https://github.com/jwhitlock/browsercompat-data
.. _`Clone project locally`: https://help.github.com/articles/which-remote-url-should-i-use/
