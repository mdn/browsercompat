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


sample_mdn.py
-------------
Load random pages from MDN in your browser.  Usage::

    $ tools/sample_mdn.py
