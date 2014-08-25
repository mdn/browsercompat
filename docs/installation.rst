============
Installation
============

Install Django App
------------------
`Note: the Django App has not been published to PyPI.  These instructions will
not work yet.`

At the command line::

    $ easy_install web-platform-compat

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv web-platform-compat
    $ pip install web-platform-compat


Install Django Project
----------------------

1. Clone project locally
2. Create virtualenv
3. Install dependencies via pip
4. Customize with environment variables (see `wpcsite/settings.py`)
5. Setup database, add superuser account (`./manage.py syncdb`)
6. Run it (`./manage.py runserver`)

Install in Heroku
-----------------

1. Clone project locally
2. `heroku apps:create`
3. `git push heroku master`
4. See current config with `heroku config`, and customize with environment
   variables using `heroku config:set` (see `wpcsite/settings.py`)
5. Add superuser account (`heroku run ./manage.py createsuperuser`)
