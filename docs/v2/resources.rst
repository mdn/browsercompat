Resources
=========

Resources are simple objects supporting CRUD_ operations.  Read operations can
be done anonymously.  Creating and updating require account permissions, and
deleting requires admin account permissions.

.. _CRUD: http://en.wikipedia.org/wiki/Create,_read,_update_and_delete

Browsers
--------

A **browser** is a brand of web client that has one or more versions.  This
follows most users' understanding of browsers, i.e., ``firefox_desktop``
represents desktop Firefox, ``safari_desktop`` represents desktop Safari, and
``firefox_android`` represents Firefox on Android.

The **browsers** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **name** *(localized)* - Browser name
    - **note** *(localized)* - Notes, intended for related data like
      OS, applicable device, engines, etc.
* **relationships**
    - **versions** *(many)* - Associated versions_, ordered roughly
      from earliest to latest.  User can change the order.
    - **history_current** *(one)* - Current historical_browsers_.  Can be
      set to a value from **history** to revert changes.
    - **history** *(many)* - Associated historical_browsers_ in time order
      (most recent first). Changes are ignored.

*Note:* `bug 1078699`_ *is proposing that select users will be able to modify slugs*

An example **browser** resource:

.. literalinclude:: /v2/raw/browser-by-id-response-body.json
    :language: json

Versions
--------

A **version** is a specific release of a Browser.

The **versions** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **version** *(write-once)* - Version of browser. Numeric or text string,
      depending on the status (see table below).
    - **release_day** - Day that browser was released in `ISO 8601`_ format, or
      null if unknown.
    - **retirement_day** - Approximate day the browser was "retired" (stopped
      being a current browser), in `ISO 8601`_ format, or null if unknown.
    - **status** - One of ``beta``, ``current``, ``future``, ``retired-beta``,
      ``retired``, or ``unknown`` (see table below).
    - **release_notes_uri** *(localized)* - URI of release notes for this
      version, or null if none.
    - **note** *(localized)* - Engine, OS, etc. information, or null
    - **order** *(read-only)* - The relative order among versions for this
      browser. The order can be changed on the **browser** resource.
* **relationships**
    - **browser** - The related **browser**
    - **supports** *(many)* - Associated **supports**, in ID order.  Changes
      are ignored; work on the **supports** to add, change, or remove.
    - **history_current** *(one)* - Current **historical_versions**.
      Set to a value from **history** to revert to that version.
    - **history** *(many)* - Associated **historical_versions**, in time
      order (most recent first).  Changes are ignored.

The version is either a numeric value, such as ``"11.0"``, or text, such as
``"Nightly"``.  The version format depends on the chosen status:

================ ================================= ===========================================================
      Status      Version                           Meaning
================ ================================= ===========================================================
``beta``         numeric                           A release candidate suggested for early adopters or testers
``current``      numeric or the text ``"current"`` A current and preferred release for most users
``future``       text such as ``"Nightly"``        A named but unnumbered future release
``retired-beta`` numeric                           An old beta version, replaced by a new beta or release
``retired``      numeric                           An old released version no longer recommended for users
``unknown``      numeric                           A release with an unknown status
================ ================================= ===========================================================

An example **version** resource:

.. literalinclude:: /v2/raw/version-by-id-response-body.json
    :language: json

Features
--------
A **feature** is a web technology.  This could be a precise technology, such
as the value ``cover`` for the CSS ``background-size`` property.  It could be
a hierarchical group of related technologies, such as the CSS
``background-size`` property or the set of all CSS properties.  Some features
correspond to a page on MDN_, which will display the list of specifications
and a browser compatibility table of the sub-features.

The **features** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **mdn_uri** *(optional, localized)* - The URI of the language-specific
      MDN page that this feature was first scraped from.  If the path contains
      unicode, it should be percent-encoded as in `RFC 3987`_. May be used in
      UX or for debugging import scripts.
    - **experimental** - True if a feature is considered experimental, such as
      being non-standard or part of an non-ratified spec.
    - **standardized** - True if a feature is described in a standards-track
      spec, regardless of the spec's maturity.
    - **stable** - True if a feature is considered suitable for production
      websites.
    - **obsolete** - True if a feature should not be used in new development.
    - **name** *(canonical or localized)* - Feature name.  If the name is the
      code used by a developer, then the value is a string, and should be
      wrapped in a ``<code>`` block when displayed.  If the name is a
      description of the feature, then the value is the available
      translations, including at least an ``en`` translation, and may include
      HTML markup.  For example, ``"display"`` and ``"display: none"`` are
      canonical names for the CSS display property and one of the values for
      that property, while ``"Basic support"``,
      ``"<code>none, inline</code> and <code>block</code>"``, and
      ``"CSS Properties"`` are non-canonical names that should be translated.

* **relationships**
    - **sections** *(many)* - Associated sections_.  Order can be changed by
      the user.
    - **supports** *(many)* - Associated supports_, Order is in ID order,
      changes are ignored.
    - **parent** *(one or null)* - The feature one level up, or null
      if top-level.  Can be changed by user.
    - **children** *(many)* - The features that have this feature as parent, in
      display order.  Can be an empty list, for "leaf" features.  Can be
      re-ordered by the user.
    - **history_current** *(one)* - Current historical_features_.  User can
      set to a valid **history** to revert to that version.
    - **history** *(many)* - Associated historical_features_, in time order
      (most recent first).  Changes are ignored.

*Note:* `bug 1240785`_ *is proposing that the slug is replaced with a list of optional aliases*

Here is an example of a leaf **feature** with a translated name:

.. literalinclude:: /v2/raw/feature-by-id-response-body.json
    :language: json

Here is an example of a branch **feature** with a canonical name (the parent of the
previous example):

.. literalinclude:: /v2/raw/feature-by-id-canonical-response-body.json
    :language: json

Supports
--------

A **support** is an assertion that a particular Version of a Browser supports
(or does not support) a feature.

The **support** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **support** - Assertion of support of the version_ for the
      feature_, one of ``"yes"``, ``"no"``, ``"partial"``, or ``"unknown"``
    - **prefix** - Prefix used to enable support, such as `"moz"`
    - **prefix_mandatory** - True if the prefix is required
    - **alternate_name** - An alternate name associated with this feature,
      such as ``"RTCPeerConnectionIdentityEvent"``
    - **alternate_name_mandatory** - True if the alternate name is required
    - **requires_config** - A configuration string
      required to enable the feature, such as
      ``"media.peerconnection.enabled=on"``
    - **default_config** - The configuration string in the shipping
      browser, such as ``"media.peerconnection.enabled=off"``
    - **protected** - True if the feature requires additional steps to enable
      in order to protect the user's security or privacy, such as geolocation
      and the Bluetooth API.
    - **note** *(localized)* - Note on support, designed for
      display after a compatibility table, can contain HTML
* **relationships**
    - **version** *(one)* - The associated version_.  Cannot be changed by
      the user after creation.
    - **feature** *(one)* - The associated feature_.  Cannot be changed by
      the user after creation.  The version and feature combo must be unique.
    - **history_current** *(one)* - Current
      historical_supports_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical_supports_
      in time order (most recent first).  Changes are ignored.


Here is a sample **support**:

.. literalinclude:: /v2/raw/support-by-id-response-body.json
    :language: json

Specifications
--------------

A **specification** is a standards document that specifies a web technology.

The **specification** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** - Unique, human-friendly key
    - **mdn_key** - Key used in the KumaScript macros SpecName_ and Spec2_.
    - **name** *(localized)* - Specification name
    - **uri** *(localized)* - Specification URI, without subpath and anchor
* **relationships**
    - **maturity** *(one)* - Associated maturity_.
      Can be changed by the user.
    - **sections** *(many)* - Associated sections_.  The order can be changed
      by the user.
    - **history_current** *(one)* - Current
      historical_specifications_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical_specifications_
      in time order (most recent first).  Changes are ignored.

Here is a sample **specification**:

.. literalinclude:: /v2/raw/specification-by-id-response-body.json
    :language: json

Sections
--------

A **section** refers to a specific area of a specification_ document.

The **section** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **number** *(optional, localized)* - The section number
    - **name** *(localized)* - Section name
    - **subpath** *(localized, optional)* - A subpage (possibly with an
      #anchor) to get to the subsection in the doc.  Can be empty string.
* **relationships**
    - **specification** *(one)* - The specification_.  Can be changed by
      the user.
    - **references** *(many)* - The associated references_.  In ID order,
      changes are ignored.
    - **history_current** *(one)* - Current
      historical_sections_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical_sections_
      in time order (most recent first).  Changes are ignored.

Here is a sample **section**:

.. literalinclude:: /v2/raw/section-by-id-response-body.json
    :language: json

References
----------

A **reference** ties a specification section_ to a feature_.

The **reference** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **note** *(localized, optional)* - Notes for this reference
* **links**
    - **feature** *(one)* - The feature. Can be changed by the user.
    - **section** *(one)* - The section. Can be changed by the user.
    - **history_current** *(one)* - Current
      historical_references_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical_references_
      in time order (most recent first).  Changes are ignored.

Here is a sample **reference**:

.. literalinclude:: /v2/raw/reference-by-id-response-body.json
    :language: json

Maturities
----------

A **maturity** refers to the maturity of a specification_ document.

The **maturity** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** - A human-friendly identifier for this maturity.  When applicable,
      it matches the key in the KumaScript macro Spec2_
    - **name** *(localized)* - Status name
* **relationships**
    - **specifications** *(many)* - Associated specifications_.  In ID order,
      changes are ignored.
    - **history_current** *(one)* - Current
      historical_maturities_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical_maturities_
      in time order (most recent first).  Changes are ignored.

Here is a sample **maturity**:

.. literalinclude:: /v2/raw/maturity-by-id-response-body.json
    :language: json

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
* **relationships**
    - **changesets** *(many)* - Associated changesets_, in ID order, changes
      are ignored.

Here's an example **user**:

.. literalinclude:: /v2/raw/user-by-id-response-body.json
    :language: json

You can also request the authenticated user's resource:

.. literalinclude:: /v2/raw/user-me-authenticated-request-headers.txt
    :language: http

The response is a redirect to the user's resource:

.. literalinclude:: /v2/raw/user-me-authenticated-response-headers.txt
    :language: http

If the request is made anonymously, then the response is an error:

.. literalinclude:: /v2/raw/user-me-anon-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/user-me-anon-response-body.json
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
* **relationships**
    - **user** *(one)* - The user_ who initiated this changeset, can not be
      changed.
    - **historical_browsers** *(many)* - Associated historical_browsers_, in ID
      order, changes are ignored.
    - **historical_features** *(many)* - Associated historical_features_,
      in ID order, changes are ignored.
    - **historical_maturities** *(many)* - Associated historical_maturities_,
      in ID order, changes are ignored.
    - **historical_sections** *(many)* - Associated historical_sections_, in ID
      order, changes are ignored.
    - **historical_specifications** *(many)* - Associated
      historical_specifications_, in ID order, changes are ignored.
    - **historical_supports** *(many)* - Associated historical_supports_, in ID
      order, changes are ignored.
    - **historical_versions** *(many)* - Associated
      historical_versions_, in ID order, changes are ignored.

Here's an example **changeset** resource:

.. literalinclude:: /v2/raw/changeset-by-id-response-body.json
    :language: json

Historical Browsers
-------------------
A **historical_browser** resource represents the state of a browser_ at a point
in time, and who is responsible for that state.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **browsers** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **browser** *(one)* - Associated browser_, can not be changed

Here is a sample **historical_browser**:

.. literalinclude:: /v2/raw/historical-browser-by-id-response-body.json
    :language: json

Historical Versions
-------------------

A **historical_versions** resource represents the state of a
version_ at a point in time, and who is responsible for that
representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **versions** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **version** *(one)* - Associated version_, can not be changed

Here is a sample **historical_version**:

.. literalinclude:: /v2/raw/historical-version-by-id-response-body.json
    :language: json

Historical Features
-------------------

A **historical_features** resource represents the state of a feature_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **features** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **feature** *(one)* - Associated feature_, can not be changed

Here is a sample **historical_feature**:

.. literalinclude:: /v2/raw/historical-feature-by-id-response-body.json
    :language: json

Historical Supports
-------------------

A **historical_supports** resource represents the state of a support_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **supports** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **support** *(one)* - Associated support_, can not be changed

Here is a sample **historical_support**:

.. literalinclude:: /v2/raw/historical-support-by-id-response-body.json
    :language: json

Historical Specifications
-------------------------

A **historical_specifications** resource represents the state of a specification_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **specifications** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **specification** *(one)* - Associated specification_, can not be changed

Here is a sample **historical_specification**:

.. literalinclude:: /v2/raw/historical-specification-by-id-response-body.json
    :language: json

Historical Sections
-------------------

A **historical_sections** resource represents the state of a section_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **sections** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **section** *(one)* - Associated section_, can not be changed

Here is a sample **historical_section**:

.. literalinclude:: /v2/raw/historical-sections-by-id-response-body.json
    :language: json

Historical References
---------------------

A **historical_references** resource represents the state of a reference_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **references** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **reference** *(one)* - Associated reference_, can not be changed

Here is a sample **historical_reference**:

.. literalinclude:: /v2/raw/historical-references-by-id-response-body.json
    :language: json

Historical Maturities
---------------------

A **historical_maturities** resource represents the state of a maturity_ at a point
in time, and who is responsible for that representation.
The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **date** *(server selected)* - The time of this change in `ISO 8601`_
    - **event** *(server selected)* - The type of event, one of ``"created"``,
      ``"changed"``, or ``"deleted"``
    - **archive_data** - The **maturities** representation at this point in time
* **relationships**
    - **changeset** *(one)* - Associated changeset_, can not be changed.
    - **maturity** *(one)* - Associated maturity_, can not be changed

Here is a sample **historical_maturity**:

.. literalinclude:: /v2/raw/historical-maturity-by-id-response-body.json
    :language: json


.. _browser: Browsers_
.. _feature: Features_
.. _specification: Specifications_
.. _section: Sections_
.. _support: Supports_
.. _reference: References_
.. _maturity: Maturities_
.. _version: Versions_
.. _user: Users_
.. _changeset: Changesets_
.. _historical_browsers: `Historical Browsers`_
.. _historical_features: `Historical Features`_
.. _historical_references: `Historical References`_
.. _historical_supports: `Historical Supports`_
.. _historical_specifications: `Historical Specifications`_
.. _historical_sections: `Historical Sections`_
.. _historical_maturities: `Historical Maturities`_
.. _historical_versions: `Historical Versions`_

.. _`bug 1078699`: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699
.. _`bug 1078699`: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699
.. _`bug 1216786`: https://bugzilla.mozilla.org/show_bug.cgi?id=1216786
.. _`bug 1240785`: https://bugzilla.mozilla.org/show_bug.cgi?id=1240785
.. _non-linguistic: http://www.w3.org/International/questions/qa-no-language#nonlinguistic
.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
.. _MDN: https://developer.mozilla.org
.. _RFC 3987: http://tools.ietf.org/html/rfc3987.html#section-3.1
.. _SpecName: https://developer.mozilla.org/en-US/docs/Template:SpecName
.. _Spec2: https://developer.mozilla.org/en-US/docs/Template:Spec2
