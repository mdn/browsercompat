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

.. literalinclude:: /v1/raw/user-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/user-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/user-by-id-response-body.json
    :language: json


You can also request the authenticated user's resource:

.. literalinclude:: /v1/raw/user-me-authenticated-request-headers.txt
    :language: http

The response is a redirect to the user's resource:

.. literalinclude:: /v1/raw/user-me-authenticated-response-headers.txt
    :language: http

If the request is made anonymously, then the response is an error:

.. literalinclude:: /v1/raw/user-me-anon-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/user-me-anon-response-body.json
    :language: json


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

.. literalinclude:: /v1/raw/changeset-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/changeset-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/changeset-by-id-response-body.json
    :language: json

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
