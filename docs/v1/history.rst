History Resources
=================

History Resources are created when a Resource is created, updated, or deleted.
By navigating the history chain, a caller can see the changes of a resource
over time.

All history representations are similar, so one example should be enough to
determine the pattern.

Historical Browsers
-------------------

A **historical_browser** resource represents the state of a browser_ at a point
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

To get a single **historical_browsers** representation:

.. literalinclude:: /v1/raw/historical-browser-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/historical-browser-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/historical-browser-by-id-response-body.json
    :language: json

Historical Versions
-------------------

A **historical_versions** resource represents the state of a
version_ at a point in time, and who is responsible for that
representation.  See historical_browsers_ and versions_ for an idea of
the representation.

Historical Features
-------------------

A **historical_features** resource represents the state of a feature_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and features_ for an idea of the representation.

Historical Sections
-------------------

A **historical_sections** resource represents the state of a section_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and sections_ for an idea of the representation.

Historical Specifications
-------------------------

A **historical_specifications** resource represents the state of a specification_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and specifications_ for an idea of the representation.

Historical Supports
-------------------

A **historical_supports** resource represents the state of a support_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and supports_ for an idea of the representation.

Historical References
---------------------

A **historical_references** resource represents the state of a reference_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and references_ for an idea of the representation.

Historical Maturities
---------------------

A **historical_maturities** resource represents the state of a maturity_ at a point
in time, and who is responsible for that representation.  See
historical_browsers_ and maturities_ for an idea of the representation.


.. _historical_browser: `Historical Browsers`_
.. _historical_browsers: `Historical Browsers`_

.. _browser: resources.html#browsers
.. _version: resources.html#versions
.. _versions: resources.html#versions
.. _support: resources.html#supports
.. _supports: resources.html#supports
.. _feature: resources.html#features
.. _features: resources.html#features
.. _maturity: resources.html#maturities
.. _maturities: resources.html#maturities
.. _specification: resources.html#specifications
.. _specifications: resources.html#specifications
.. _section: resources.html#sections
.. _sections: resources.html#sections
.. _reference: resources.html#references
.. _references: resources.html#references

.. _changeset: change-control#changesets

.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
