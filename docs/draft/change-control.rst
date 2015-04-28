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
    - **created** *(server selected)* - Time that the account was created, in
      `ISO 8601`_ format.
    - **agreement** - The version of the contribution agreement the
      user has accepted.  "0" for not agreed, "1" for first version, etc.
    - **permissions** - A list of permissions.  Permissions include
      ``"change-resource"`` (add or change any resource except users_ or
      history resources),
      ``"delete-resource"`` (delete any resource)
      ``"import-mdn"`` (setup import of an MDN page)
* **links**
    - **changesets** *(many)* - Associated changesets_, in ID order, changes
      are ignored.

To get a single **user** representation:

.. code-block:: http

    GET /api/v1/users/42 HTTP/1.1
    Host: browsersupports.org
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
            "created": "2014-07-10T13:55:51.750Z",
            "agreement": "1",
            "permissions": ["change-resource"],
            "links": {
                "changesets": ["73"]
            }
        },
        "links": {
            "users.changesets": {
                "href": "https://browsersupports.org/api/v1/changesets/{users.changesets}",
                "type": "changesets"
            }
        }
    }

If a client is authenticated, the logged-in user's account can be retrieved with:

.. code-block:: http

    GET /api/v1/users/me HTTP/1.1
    Host: browsersupports.org
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
    - **created** *(server selected)* - When the changeset was created, in
      `ISO 8601`_ format.
    - **modified** *(server selected)* - When the changeset was last modified,
      in `ISO 8601`_ format.
    - **target_resource_type** *(write-once, optional)* - The name of the
      primary resource for this changeset, for example "browsers", "versions",
      etc.
    - **target_resource_id** *(write-once, optional)* - The ID of the primary
      resource for this changeset.
    - **closed** - True if the changeset is closed to new changes.
      Auto-created changesets are auto-closed, and cache invalidation is
      delayed until manually created changesets are closed.
* **links**
    - **user** *(one)* - The user who initiated this changeset, can not be
      changed.
    - **historical_browsers** *(many)* - Associated historical_browsers_, in ID
      order, changes are ignored.
    - **historical_features** *(many)* - Associated historical_features_,
      in ID order, changes are ignored.
    - **historical_maturities** *(many)* - Associated historical_maturities_,
      in ID order, changes are ignored.
    - **historical_sections** *(many)* - Associated historical_sections_, in ID
      order, changes are ignored.
    - **historical_specificationss** *(many)* - Associated
      historical_specificationss_, in ID order, changes are ignored.
    - **historical_supports** *(many)* - Associated historical_supports_, in ID
      order, changes are ignored.
    - **historical_versions** *(many)* - Associated
      historical_versions_, in ID order, changes are ignored.


To get a single **changeset** representation:

.. code-block:: http

    GET /api/v1/changeset/73 HTTP/1.1
    Host: browsersupports.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "changesets": {
            "id": "73",
            "created": "2014-07-14T15:50:48.910Z",
            "modified": "2014-07-14T15:50:48.910Z",
            "closed": true,
            "target_resource_type": "features",
            "target_resource_id": "35",
            "links": {
                "user": "42",
                "historical_browsers": [],
                "historical_features": [],
                "historical_maturities": [],
                "historical_sections": [],
                "historical_specifications": [],
                "historical_supports": ["1789", "1790"],
                "historical_versions": []
            }
        },
        "links": {
            "changesets.user": {
                "href": "https://browsersupports.org/api/v1/users/{changesets.user}",
                "type": "users"
            },
            "changesets.historical_browsers": {
                "href": "https://browsersupports.org/api/v1/historical_browsers/{changesets.historical_browsers}",
                "type": "historical_browsers"
            },
            "changesets.historical_features": {
                "href": "https://browsersupports.org/api/v1/historical_features/{changesets.historical_features}",
                "type": "historical_features"
            },
            "changesets.historical_maturities": {
                "href": "https://browsersupports.org/api/v1/historical_maturities/{changesets.historical_maturities}",
                "type": "historical_maturities"
            },
            "changesets.historical_sections": {
                "href": "https://browsersections.org/api/v1/historical_sections/{changesets.historical_sections}",
                "type": "historical_sections"
            },
            "changesets.historical_specifications": {
                "href": "https://browserspecifications.org/api/v1/historical_specifications/{changesets.historical_specifications}",
                "type": "historical_specifications"
            },
            "changesets.historical_supports": {
                "href": "https://browsersupports.org/api/v1/historical_supports/{changesets.historical_supports}",
                "type": "historical_supports"
            },
            "changesets.historical_versions": {
                "href": "https://browsersupports.org/api/v1/historical_versions/{changesets.historical_versions}",
                "type": "historical_versions"
            }
        }
    }

.. _user: Users_

.. _support: resources.html#supports

.. _historical_browsers: history.html#historical-browsers
.. _historical_features: history.html#historical-features
.. _historical_maturities: history.html#historical-maturities
.. _historical_sections: history.html#historical-sections
.. _historical_specificationss: history.html#historical-specificationss
.. _historical_supports: history.html#historical-supports
.. _historical_versions: history.html#historical-versions

.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
