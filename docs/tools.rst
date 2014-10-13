Tools
=====

Some potentially useful scripts can be found in the /tools folder:

load_webcompat_data.py
----------------------
Initialize with compatability data from the webcompat project. Usage::

    $ tools/load_webcompat_data.py [--api <API>] [--user <USER>] [-v]

* ``--api <API>`` `(optional)`: Set the base URL of the API
  (default: `http://localhost:8000`)
* ``--user <USER>`` `(optional)`: Set the username to use on the API
  (default: prompt for username)
* ``-v`` `(optional)`: Increase verbosity.  Can be added multiple times.  At least one is
  recommended.

This script requires a fresh database (no compatability data) and a user with
write access.  The bulk import will result in cascading cache invalidations,
which can be avoided by running the server without cached instances during the
import::

    $ USE_INSTANCE_CACHE=0 ./manage.py runserver


sample_mdn.py
-------------
Load random pages from MDN in your browser.  Usage::

    $ tools/sample_mdn.py
