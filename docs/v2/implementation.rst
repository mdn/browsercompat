Implementation
--------------

The v2 API implements the `JSON API v1.0`_ specification. This section shows
how to interact with the API, and the next section gives the details of the
resources available through the API.

Resources
*********
Resources are identified by a plural noun.  The list of resources,
available at https://browsercompat.herokuapp.com/api/v2, include:

* **browsers** - A brand of web client with one of more versions
* **versions** - A specific release of a browser
* **features** - A web technology
* **supports** - Support details of a version for a feature
* **specifications** - A document specifying a web technology
* **maturities** - The state of a specification in the standardization process
* **sections** - A section of a specification
* **references** - The link from a section to a feature
* **changesets** - A collection of one or more data changes
* **users** - API users
* **historical_browsers** - A change to a browser resource
* **historical_versions** - A change to a version resource
* **historical_features** - A change to a feature resource
* **historical_supports** - A change to a support resource
* **historical_specifications** - A change to a specification resource
* **historical_maturities** - A change to a maturity resource
* **historical_sections** - A change to a section resource

There is also a view that combines related resources:

* **view_features** - A feature combined with related resources.

List
****
To request a paginated list of a resource, ``GET`` the resource by name:

.. literalinclude:: /v2/raw/browser-list-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/browser-list-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-list-response-body.json
    :language: json

Retrieve by ID
**************
To request a single resource, ``GET`` by name and ID.

*Note:* `bug 1230306`_ *proposes switching IDs to UUIDs.*

Here's an example:

.. literalinclude:: /v2/raw/browser-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/browser-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-by-id-response-body.json
    :language: json

Filter by attribute
*******************
*Note:* `bug 1078699`_ *proposes an alternate URL format for retrieving by slug.*

Resources can be filtered by an attribute value, using a filter query string:

.. literalinclude:: /v2/raw/browser-filter-by-slug-request-headers.txt
    :language: http

The response includes the desired browser, in list format:

.. literalinclude:: /v2/raw/browser-filter-by-slug-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-filter-by-slug-response-body.json
    :language: json

Fetch Related Resources
***********************
Related resources appear in the JSON under /data/relationships. The "related"
link can be used to get the related resources:

.. literalinclude:: /v2/raw/browser-related-versions-request-headers.txt
    :language: http

The response includes the related data, as a list of resources or a single
resource, depending on the relationship:

.. literalinclude:: /v2/raw/browser-related-versions-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-related-versions-response-body.json
    :language: json

Fetch Relationships
*******************
Alternatively, just the data for a relationship can be retrieved using the
"self" link of related resources:

.. literalinclude:: /v2/raw/browser-relationships-versions-request-headers.txt
    :language: http

The response just includes the types and IDs of the related resources:

.. literalinclude:: /v2/raw/browser-relationships-versions-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-relationships-versions-response-body.json
    :language: json

Create a Single Resource
************************
To create a new resource, ``POST`` to the resource list as an authenticated
user. The ``POST`` body must include at least the required attributes.  Some
items (such as the ``history_current`` ID) will be picked by the server, and
will be ignored if included.

Here is an example creating a browser with minimal data:

.. literalinclude:: /v2/raw/browser-create-minimal-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-minimal-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/browser-create-minimal-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-minimal-response-body.json
    :language: json


Create Multiple Resources
*************************
When creating several resources, the changes can be associated by first
creating a changeset:


.. literalinclude:: /v2/raw/browser-create-in-changeset-1-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-1-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/browser-create-in-changeset-1-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-1-response-body.json
    :language: json

The changeset can then be specified as a query parameter:

.. literalinclude:: /v2/raw/browser-create-in-changeset-2-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-2-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/browser-create-in-changeset-2-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-2-response-body.json
    :language: json

Finally, close the changeset, which is now associated with the historical
resources:

.. literalinclude:: /v2/raw/browser-create-in-changeset-3-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-3-request-body.json
    :language: json

The response includes relationships to the items created in the changeset:

.. literalinclude:: /v2/raw/browser-create-in-changeset-3-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-create-in-changeset-3-response-body.json
    :language: json

.. _`JSON API v1.0`: http://jsonapi.org/format/1.0/

Update a resource
*****************
To update a resource with new data, ``PATCH`` the instance with the new data.
Omitted items with keep their old values. For each resource, there are some
items that can not be changed (for example, the ``id`` or the ``history``
relationship IDs), and will be ignored if included in the update request. A
successful update will return a ``200 OK``, add a new ID to the ``history``
relationship, and update the ``history_current`` relationship.

Here's an example of updating a browser:

.. literalinclude:: /v2/raw/browser-update-partial-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-update-partial-request-body.json
    :language: json

With this response:

.. literalinclude:: /v2/raw/browser-update-partial-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/browser-update-partial-response-body.json
    :language: json

Update a one-to-many relationship
*********************************
Some relationships are one-to-many, and the relationship appears on both sides.
For example, a specification has one maturity, but a maturity can be related
to several specifications. To update these relationships, ``PATCH`` the "to-one"
relationship (maturity) on the "many" resource (specification):

.. literalinclude:: /v2/raw/specification-update-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/specification-update-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/specification-update-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/specification-update-response-body.json
    :language: json

Update a relationship via relationship link
*******************************************
An alternate way to change a relationship is to ``PATCH`` the relationship
endpoint:

.. literalinclude:: /v2/raw/specification-relationships-maturity-update-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/specification-relationships-maturity-update-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/specification-relationships-maturity-update-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/specification-relationships-maturity-update-response-body.json
    :language: json

Update the order of a one-to-many relationship
**********************************************
For some one-to-many relationships, the order of the to-many relationships
matters (for example, version order with respect to browsers, and child
features with respect to the parent feature). To change the order, update the
order of the relationships on the "one" resource, either by updating the
resource or the relationship:

.. literalinclude:: /v2/raw/feature-set-relationship-children-order-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/feature-set-relationship-children-order-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/feature-set-relationship-children-order-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/feature-set-relationship-children-order-response-body.json
    :language: json

Revert to previous revision
***************************
To revert an instance to a previous revision, set the ``history_current``
relationship to the history ID of the previous revision.  This resets the
content and creates a new history object for the change:

.. literalinclude:: /v2/raw/feature-revert-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/feature-revert-request-body.json
    :language: json

A sample response is:

.. literalinclude:: /v2/raw/feature-revert-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/feature-revert-response-body.json
    :language: json

Delete a resource
*****************
To delete a resource:

.. literalinclude:: /v1/raw/version-delete-request-headers.txt
    :language: http

The response has no body:

.. literalinclude:: /v1/raw/version-delete-response-headers.txt
    :language: http

Revert a deletion
*****************
Reverting deletions is not currently possible, and is tracked in `bug 1159349`_.

.. _`bug 1078699`: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699
.. _`bug 1159349`: https://bugzilla.mozilla.org/show_bug.cgi?id=1159349
.. _`bug 1230306`: https://bugzilla.mozilla.org/show_bug.cgi?id=1230306
