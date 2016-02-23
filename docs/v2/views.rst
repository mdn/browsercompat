Views
=====

A **View** is a combination of resources for a particular presentation.  It is
suitable for anonymous viewing of content. It uses the flexibility of the
JSON API specification to include a basket of related resources in a response,
but doesn't use the official method of `Inclusion of Related Resources`_.

View a Feature
~~~~~~~~~~~~~~

This view collects the data for a feature_, including the related
resources needed to display it on MDN.

Here is a simple example, the view for the CSS property float_:

.. literalinclude:: /v2/raw/view-feature-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/view-feature-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-by-id-response-body.json
    :language: json

Generating a Compatibility Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
One way to use this representation is:

1. Parse /data and /included into an in-memory object store, so that you can
   load a resource given the type and ID.
2. Create the "Specifications" section:
    1. Add the ``Specifications`` header
    2. Create an HTML table with a header row "Specification", "Status", "Comment"
    3. For each id in /data/relationships/sections (``"1"``, ``"2"``, ``"3"```):
        * Load the section, specification, and maturity
        * Add the first column: a link to
          (specification).attributes.uri.(lang or en) +
          (section).attributes.subpath.(lang or en), with link text
          (specification).attributes.name.(lang or en), with title based on
          (section).attributes.name.(lang or en) or
          data.attributes.name.(lang or en).
        * Add the second column: A span with class
          "spec-" + (maturity).attributes.slug, and the text
          (maturity).attributes.name.(lang or en).
        * Add the third column:
          (maturity).attributes.notes.(lang or en), or empty string
    4. Close the table, and add an edit button.
3. Create the Browser Compatibility section:
    1. Add The "Browser compatibility" header
    2. For each item in /meta/compat_table/tabs:
        * Create a table with the proper name ("Desktop", "Mobile")
        * Load the browser by ID in /browsers
        * Add a column the translated browser name
    3. For the main feature in /data and each feature in /data/relationships/children:
        * Add the first column: the feature name (attributes/name).  If it is a string, then wrap
          in ``<code>``.  Otherwise, use the best translation of name,
          in a ``lang=(lang)`` block. A good name for the main feature is
          "Basic Support".
        * Add any feature flags, such as an obsolete or experimental icon,
          based on the feature flags.
        * Load the supports reference list in
          /meta/compat_table/supports/(feature ID)/(browser ID)/(support IDs)
        * For each browsers' supports reference list:
            - If no supports, then display "?"
            - If just one support, display "<``version``>", or "<``support``>",
              depending on the defined attributes
            - If multiple supports, display as subcells
            - Add prefixes, alternate names, config, and notes link
              as appropriate
    4. Close each table, add an edit button
    5. Add notes for displayed supports

This may be done by including the JSON in the page as sent over the wire,
or loaded asynchronously, with the tables built after initial page load.

This can also be used by a `"caniuse" table layout`_ by ignoring the meta
section and displaying all the included data.  This will require more
client-side processing to generate, or additional data in the ``<meta>``
section.

Including Child Pages
---------------------
By default, ``view_feature`` only includes *row children*, which are
subfeatures that are represented as rows in the MDN table.  These row children
are identified by not having a value for ``mdn_uri``.

There can also be *page children*, which are represented as more detailed
page on MDN.  For example, *Web/CSS* has the page child *Web/CSS/Display*.
By default, these are not included, but can be included by setting the query
parameter ``child_pages=1``:

.. literalinclude:: /v2/raw/view-feature-by-id-with-child-pages-request-headers.txt
    :language: http


Updating Views with Changesets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating the page requires a sequence of requests.  For example, if a user
wants to change Chrome support for ``<address>`` from an unknown version to
version 2, you'll have to create the version_ for that version,
then add the support_ for the support.

The first step is to create a changeset_ as an authenticated user:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-1-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-1-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-1-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-1-response-body.json
    :language: json

Next, use the changeset_ ID when creating the version_:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-2-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-2-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-2-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-2-response-body.json
    :language: json

Finally, create the support_:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-3-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-3-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-3-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-parts-with-changeset-3-response-body.json
    :language: json

The historical_versions_ and historical_supports_
resources will both refer to changeset_ 56, and this changeset_ is
linked to feature_ 6, despite the fact that no changes were made
to the feature_.  This will facilitate displaying a history of
the compatibility tables, for the purpose of reviewing changes and reverting
vandalism.

Updating View with PATCH
~~~~~~~~~~~~~~~~~~~~~~~~

``view_features`` supports PATCH for bulk updates of support data.  Here is a simple
example that adds a new subfeature without support:

.. literalinclude:: /v2/raw/view-feature-update-put-subfeature-request-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-put-subfeature-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v2/raw/view-feature-update-put-subfeature-response-headers.txt
    :language: http

.. literalinclude:: /v2/raw/view-feature-update-put-subfeature-response-body.json
    :language: json

The response is the feature view with new and updated items, or an error
response.

This is a trivial use case, which would be better implemented by creating the
feature_ directly, but it can be extended to bulk updates of existing feature
views, or for first-time importing of subfeatures and support data.  It has
some quirks:

* New items should be identified with an ID starting with an underscore
  (``_``).  Relations to new items should use the underscored IDs.
* Only feature_, reference_, section_, and support_ resources can be added or
  updated.  Features must be the target feature or a descendant, and other
  resources must be restricted to those features or a valid new feature..
* Deletions are not supported.
* Other resources (browsers_, versions_, etc) can not be added or changed.
  This includes adding links to new resources.

Once the MDN import is complete, this PATCH interface will be deprecated in
favor of direct POST and PATCH to the standard resource API.

.. _browsers: resources.html#browsers
.. _feature: resources.html#features
.. _reference: resources.html#references
.. _section: resources.html#sections
.. _support: resources.html#supports
.. _version: resources.html#versions
.. _versions: resources.html#versions

.. _changeset: resources.html#changeset

.. _historical_versions: resources.html#historical-versions
.. _historical_supports: resources.html#historical-supports

.. _float: https://developer.mozilla.org/en-US/docs/Web/CSS/float
.. _`Inclusion of Related Resources`: http://jsonapi.org/format/#fetching-includes
.. _`"caniuse" table layout`: https://wiki.mozilla.org/MDN/Development/CompatibilityTables/Data_Requirements#1._CanIUse_table_layout
