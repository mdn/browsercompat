History Resources
=================

History Resources are created when a Resource is created, updated, or deleted.
By navigating the history chain, a caller can see the changes of a resource
over time.

All history representations are similar, so one example should be enough to
determine the pattern.

Browsers History
----------------

A **browsers-history** represents the state of a browser_ at a point in
time, and who is responsible for that state.  The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **timestamp** *(server selected)* - Timestamp of this change
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **browsers** - The **browsers** representation at this point in time
* **links**
    - **browser** *(one)* - Associated browser_, can not be changed
    - **changeset** *(one)* - Associated changeset_, can not be changed.

To get a single **browsers-history** representation:

.. code-block:: http

    GET /browsers-history/1002 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers-history": {
            "id": "1002",
            "timestamp": "1404919464.559140",
            "event": "created",
            "browsers": {
                "id": "2",
                "slug": "firefox",
                "environment": "desktop",
                "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
                "name": {
                    "en": "Firefox"
                },
                "engine": {
                    "en": "Gecko"
                },
                "links": {
                    "versions": ["124"],
                    "history-current": "1002",
                    "history": ["1002"]
                }
            },
            "links": {
                "browser": "1",
                "changeset": "1",
            }
        },
        "links": {
            "browsers-history.browser": {
                "href": "https://api.compat.mozilla.org/browser-history/{browsers-history.browser}",
                "type": "browsers"
            },
            "browsers-history.changeset": {
                "href": "https://api.compat.mozilla.org/changesets/{browsers-history.changeset}",
                "type": "changeset"
            }
        }
    }

Browser Versions History
------------------------

A **browser-versions-history** represents a state of a browser-version_ at
a point in time, and who is responsible for that representation.  See
browsers-history_ and browser-versions_ for an idea of the represention.

Features History
----------------

A **features-history** represents a state of a feature_ at a point in time,
and who is responsible for that representation.  See browsers-history_ and
features_ for an idea of the represention.

Feature Sets History
--------------------

A **feature-sets-history** represents a state of a feature-set_ at a point
in time, and who is responsible for that representation.  See
browsers-history_ and feature-sets_ for an idea of the represention.

Browser Version Features History
--------------------------------

A **browser-version-features-history** represents a state of a
browser-version-feature_ at a point in time, and who is responsible for that
representation.  See browsers-history_ and browser-version-features_ for
an idea of the represention.

.. _browsers-history: `Browsers History`_

.. _browser: resources.html#browsers
.. _browser-version: resources.html#browser-versions
.. _browser-versions: resources.html#browser-versions
.. _browser-version-feature: resources.html#browser-versions-feature
.. _browser-version-features: resources.html#browser-versions-features
.. _feature: resources.html#features
.. _features: resources.html#features
.. _feature-set: resources.html#feature-sets
.. _feature-sets: resources.html#feature-sets

.. _changeset: change-control#changesets
