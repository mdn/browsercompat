History Resources
=================

History Resources are created when a Resource is created, updated, or deleted.
By navigating the history chain, a caller can see the changes of a resource
over time.

All history representations are similar, so one example should be enough to
determine the pattern.

Historical Browsers
-------------------

A **historical-browser** resource represents the state of a browser_ at a point
in time, and who is responsible for that state.  The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **browsers** - The **browsers** representation at this point in time
* **links**
    - **browser** *(one)* - Associated browser_, can not be changed
    - **changeset** *(one)* - Associated changeset_, can not be changed.

To get a single **historical-browsers** representation:

.. code-block:: http

    GET /historical-browsers/1002 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "historical-browsers": {
            "id": "1002",
            "timestamp": "1404919464.559140",
            "event": "created",
            "browsers": {
                "id": "2",
                "slug": "firefox",
                "icon": "https://compat.cdn.mozilla.net/media/img/browsers/firefox.png",
                "name": {
                    "en": "Firefox"
                },
                "note": {
                    "en": "Uses Gecko for its web browser engine."
                },
                "links": {
                    "history-current": "1002",
                }
            },
            "links": {
                "browser": "1",
                "changeset": "1",
            }
        },
        "links": {
            "historical-browsers.browser": {
                "href": "https://api.compat.mozilla.org/browser-history/{historical-browsers.browser}",
                "type": "browsers"
            },
            "historical-browsers.changeset": {
                "href": "https://api.compat.mozilla.org/changesets/{historical-browsers.changeset}",
                "type": "changeset"
            }
        }
    }

Historical Browser Versions
---------------------------

A **historical-browser-versions** resource represents the state of a
browser-version_ at a point in time, and who is responsible for that
representation.  See historical-browsers_ and browser-versions_ for an idea of
the represention.

Historical Features
-------------------

A **historical-features** resource represents the state of a feature_ at a point
in time, and who is responsible for that representation.  See
historical-browsers_ and features_ for an idea of the represention.

Historical Browser Version Features
-----------------------------------

A **historical-browser-version-features** resource represents a state of a
browser-version-feature_ at a point in time, and who is responsible for that
representation.  See historical-browsers_ and browser-version-features_ for an
idea of the represention.

.. _historical-browser: `Historical Browsers`_
.. _historical-browsers: `Historical Browsers`_

.. _browser: resources.html#browsers
.. _browser-version: resources.html#browser-versions
.. _browser-versions: resources.html#browser-versions
.. _browser-version-feature: resources.html#browser-versions-feature
.. _browser-version-features: resources.html#browser-versions-features
.. _feature: resources.html#features
.. _features: resources.html#features

.. _changeset: change-control#changesets

.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
