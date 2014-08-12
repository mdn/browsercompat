Change Control Resources
========================

Change Control Resources help manage changes to resources.

Users
-----

A **user** represents a person or process that creates, changes, or deletes a
resource.

The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **username** - The user's email or ID
    - **created** *(server selected)* - UTC timestamp of when this user
      account was created
    - **agreement-version** - The version of the contribution agreement the
      user has accepted.  "0" for not agreed, "1" for first version, etc.
    - **permissions** - A list of permissions.  Permissions include
      ``"change-browser-version-feature"`` (add or change a browser-version-feature_)
      ``"change-resource"`` (add or change any resource except users_ or
      history resources)
      ``"change-user"`` (change a user_ resource)
      ``"delete-resource"`` (delete any resource)
* **links**
    - **changesets** *(many)* - Associated changesets_, in ID order, changes
      are ignored.

To get a single **user** representation:

.. code-block:: http

    GET /users/42 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "users": {
            "id": "42",
            "username": "askDNA@tdv.com",
            "created": "1405000551.750000",
            "agreement-version": "1",
            "permissions": ["change-browser-version-feature"],
            "links": {
                "changesets": ["73"]
            }
        },
        "links": {
            "users.changesets": {
                "href": "https://api.compat.mozilla.org/changesets/{users.changesets}",
                "type": "changesets"
            }
        }
    }

If a client is authenticated, the logged-in user's account can be retrieved with:

.. code-block:: http

    GET /users/me HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

Changesets
----------

A **changeset** collects history resources into a logical unit, allowing for
faster reversions and better history display.  The **changeset** can be
auto-created through a ``POST``, ``PUT``, or ``DELETE`` to a resource, or it
can be created independently and specified by adding ``changeset=<ID>`` URI
parameter (i.e., ``PUT /browsers/15?changeset=73``).

The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **created** *(server selected)* - UTC timestamp of when this changeset
      was created
    - **modified** *(server selected)* - UTC timestamp of when this changeset
      was last modified
    - **target-resource** *(write-once)* - The name of the primary resource
      for this changeset, for example "browsers", "browser-versions", etc.
    - **target-resource-id** *(write-once)* - The ID of the primary resource
      for this changeset.
* **links**
    - **user** *(one)* - The user who initiated this changeset, can not be
      changed.
    - **browsers-history** *(many)* - Associated browsers-history_, in ID
      order, changes are ignored.
    - **browser-versions-history** *(many)* - Associated
      browser-versions-history_, in ID order, changes are ignored.
    - **features-history** *(many)* - Associated features-history_,
      in ID order, changes are ignored.
    - **feature-sets-history** *(many)* - Associated feature-sets-history_,
      in ID order, changes are ignored.
    - **browser-version-features-history** *(many)* - Associated
      browser-version-features-history_, in ID order, changes are ignored.


To get a single **changeset** representation:

.. code-block:: http

    GET /changeset/73 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "changesets": {
            "id": "73",
            "created": "1405353048.910000",
            "modified": "1405353048.910000",
            "target-resource": "feature-sets",
            "target-resource-id": "35",
            "links": {
                "user": "42",
                "browsers-history": [],
                "browser-versions-history": [],
                "features-history": [],
                "feature-sets-history": [],
                "browser-version-features-history": ["1789", "1790"]
            }
        },
        "links": {
            "changesets.user": {
                "href": "https://api.compat.mozilla.org/users/{changesets.user}",
                "type": "users"
            },
            "changesets.browsers-history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{changesets.browsers-history}",
                "type": "browsers-history"
            },
            "changesets.browser-versions-history": {
                "href": "https://api.compat.mozilla.org/browser-versions-history/{changesets.browser-versions-history}",
                "type": "browser-versions-history"
            },
            "changesets.features-history": {
                "href": "https://api.compat.mozilla.org/features-history/{changesets.features-history}",
                "type": "features-history"
            },
            "changesets.feature-sets-history": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{changesets.feature-sets-history}",
                "type": "feature-sets-history"
            },
            "changesets.browser-version-features-history": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{changesets.browser-version-features-history}",
                "type": "browser-version-features-history"
            }
        }
    }

.. _user: Users_

.. _browser-version-feature: resources.html#browser-version-features

.. _browsers-history: history.html#browsers-history
.. _browser-versions-history: history.html#browser-versions-history
.. _browser-version-features-history: history.html#browser-version-features-history
.. _features-history: history.html#features-history
.. _feature-sets-history: history.html#feature-sets-history
