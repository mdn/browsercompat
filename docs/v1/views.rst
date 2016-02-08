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

.. literalinclude:: /v1/raw/view-feature-by-id-request-headers.txt
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/view-feature-by-id-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-by-id-response-body.json
    :language: json

One way to use this representation is:

1. Parse into an in-memory object store,
2. Create the "Specifications" section:
    1. Add the ``Specifications`` header
    2. Create an HTML table with a header row "Specification", "Status", "Comment"
    3. For each id in features.links.sections (``["746", "421", "70"]``):
        * Add the first column: a link to specifications.uri.(lang or en) +
          sections.subpath.(lang or en), with link text
          specifications.name.(lang or en), with title based on
          sections.name.(lang or en) or feature.name.(lang or en).
        * Add the second column: A span with class
          "spec-" + maturities.slug, and the text
          maturities.name.(lang or en).
        * Add the third column:
          maturities.notes.(lang or en), or empty string
    4. Close the table, and add an edit button.
3. Create the Browser Compatibility section:
    1. Add The "Browser compatibility" header
    2. For each item in meta.compat_table.tabs, create a table with the proper
       name ("Desktop", "Mobile")
    3. For each browser id in meta.compat-table.tabs.browsers, add a column with
       the translated browser name.
    4. For each feature in features.features:
        * Add the first column: the feature name.  If it is a string, then wrap
          in ``<code>``.  Otherwise, use the best translation of feature.name,
          in a ``lang=(lang)`` block.
        * Add any feature flags, such as an obsolete or experimental icon,
          based on the feature flags.
        * For each browser id in meta.compat-table-important:
            - Get the important support IDs from
              meta.compat-table-important.supports.<``feature ID``>.<``browser ID``>
            - If null, then display "?"
            - If just one, display "<``version``>", or "<``support``>",
              depending on the defined attributes
            - If multiple, display as subcells
            - Add prefixes, alternate names, config, and notes link
              as appropriate
    5. Close each table, add an edit button
    6. Add notes for displayed supports

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

.. literalinclude:: /v1/raw/view-feature-by-id-with-child-pages-request-headers.txt
    :language: http


Updating Views with Changesets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating the page requires a sequence of requests.  For example, if a user
wants to change Chrome support for ``<address>`` from an unknown version to
version 1, you'll have to create the version_ for that version,
then add the support_ for the support.

The first step is to create a changeset_ as an authenticated user:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-1-request-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-1-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-1-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-1-response-body.json
    :language: json

Next, use the changeset_ ID when creating the version_:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-2-request-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-2-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-2-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-2-response-body.json
    :language: json

Finally, create the support_:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-3-request-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-3-request-body.json
    :language: http

A sample response is:

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-3-response-headers.txt
    :language: http

.. literalinclude:: /v1/raw/view-feature-update-parts-with-changeset-3-response-body.json
    :language: json

The historical_versions_ and historical_supports_
resources will both refer to changeset_ 36, and this changeset_ is
linked to feature_ 5, despite the fact that no changes were made
to the feature_.  This will facilitate displaying a history of
the compatibility tables, for the purpose of reviewing changes and reverting
vandalism.

Updating View with PUT
~~~~~~~~~~~~~~~~~~~~~~

``view_features`` supports PUT for bulk updates of support data.  Here is a simple
example that adds a new subfeature without support:

.. code-block:: http

    PUT /api/v1/view_features/html-element-address HTTP/1.1
    Host: browsercompat.org
    Content-Type: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

.. code-block:: json

    {
        "features": {
            "id": "816",
            "slug": "html-element-address",
            "mdn_uri": {
                "en": "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address"
            },
            "experimental": false,
            "standardized": true,
            "stable": true,
            "obsolete": false,
            "name": "address",
            "links": {
                "sections": ["746", "421", "70"],
                "supports": [],
                "parent": "800",
                "children": ["191"],
                "history_current": "216",
                "history": ["216"]
            }
        },
        "linked": {
            "features": [
                {
                    "id": "_New Subfeature",
                    "slug": "html-address-new-subfeature",
                    "name": {
                        "en": "New Subfeature"
                    },
                    "links": {
                        "parent": "816"
                    }
                }
            ]
        }
    }

The response is the feature view with new and updated items, or an error
response.

This is a trivial use case, which would be better implemented by creating the
feature_ directly, but it can be extended to bulk updates of existing feature
views, or for first-time importing of subfeatures and support data.  It has
some quirks:

* New items should be identified with an ID starting with an underscore
  (``_``).  Relations to new items should use the underscored IDs.
* Only feature_, support_, and section_ resources can be added or updated.
  Features must be the target feature or a descendant, and supports and
  sections are restricted to those features.
* Deletions are not supported.
* Other resources (browsers_, versions_, etc) can not be added or changed.
  This includes adding links to new resources.

Once the MDN import is complete, this PUT interface will be deprecated in
favor of direct POST and PUT to the standard resource API.

.. _browsers: resources.html#browsers
.. _feature: resources.html#features
.. _section: resources.html#sections
.. _support: resources.html#supports
.. _version: resources.html#versions
.. _versions: resources.html#versions

.. _changeset: change-control#changeset

.. _historical_versions: history.html#historical-versions
.. _historical_supports: history.html#historical-supports

.. _float: https://developer.mozilla.org/en-US/docs/Web/CSS/float
.. _`Inclusion of Related Resources`: http://jsonapi.org/format/#fetching-includes
.. _`"caniuse" table layout`: https://wiki.mozilla.org/MDN/Development/CompatibilityTables/Data_Requirements#1._CanIUse_table_layout
