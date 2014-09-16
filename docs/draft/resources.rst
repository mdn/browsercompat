Resources
=========

Resources are simple objects supporting CRUD_ operations.  Read operations can
be done anonymously.  Creating and updating require account permissions, and
deleting requires admin account permissions.

All resources support similar operations using HTTP methods:

* ``GET /<type>`` - List instances (paginated)
* ``POST /<type>`` - Create new instance
* ``GET /<type>/<id>`` - Retrieve an instance
* ``PUT /<type>/<id>`` - Update an instance
* ``DELETE /<type>/<id>`` - Delete instance

Additional features may be added as needed.  See the `JSON API docs`_ for ideas
and what format they will take.

Because the operations are similar, only browsers_ has complete operations
examples, and others just show retrieving an instance (``GET /<type>/<id>``).

.. _CRUD: http://en.wikipedia.org/wiki/Create,_read,_update_and_delete
.. _`JSON API docs`: http://jsonapi.org/format/

.. contents:: 

Browsers
--------

A **browser** is a brand of web client that has one or more versions.  This
follows most users' understanding of browsers, i.e., ``firefox`` represents
desktop Firefox, ``safari`` represents desktop Safari, and ``firefox-mobile``
represents Firefox Mobile.

The **browsers** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **icon** - Secure URI (https) of representative icon
    - **name** *(localized)* - Browser name
    - **note** *(localized)* - Notes, intended for related data like
      OS, applicable device, engines, etc.
* **links**
    - **versions** *(many)* - Associated versions_, ordered roughly
      from earliest to latest.  User can change the order.
    - **history-current** *(one)* - Current historical-browsers_.  Can be
      set to a value from **history** to revert changes.
    - **history** *(many)* - Associated historical-browsers_ in time order
      (most recent first). Changes are ignored.


List
****

To request the paginated list of **browsers**:

.. code-block:: http

    GET /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": [{
            "id": "1",
            "slug": "chrome",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/chrome.png",
            "name": {
                "en": "Chrome"
            },
            "note": null,
            "links": {
                "versions": ["123", "758"],
                "history-current": "1001",
                "history": ["1001"]
            }
        },{
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
                "versions": ["124", "759"],
                "history-current": "1002",
                "history": ["1002"]
            }
        },{
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "Internet Explorer"
            },
            "note": null,
            "links": {
                "versions": ["125", "167", "178", "760"],
                "history-current": "1003",
                "history": ["1003"]
            }
        },{
            "id": "4",
            "slug": "opera",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/opera.png",
            "name": {
                "en": "Opera"
            },
            "note": null,
            "links": {
                "versions": ["126", "761"],
                "history-current": "1004",
                "history": ["1004"]
            }
        },{
            "id": "5",
            "slug": "safari",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/safari.png",
            "name": {
                "en": "Safari"
            },
            "note": {
                "en": "Uses Webkit for its web browser engine."
            },
            "links": {
                "versions": ["127", "762"],
                "history-current": "1005",
                "history": ["1005"]
            }
        },{
            "id": "6",
            "slug": "android",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/android.png",
            "name": {
                "en": "Android"
            },
            "note": null,
            "links": {
                "versions": ["128", "763"],
                "history-current": "1006",
                "history": ["1006"]
            }
        },{
            "id": "7",
            "slug": "firefox-mobile",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/firefox-mobile.png",
            "name": {
                "en": "Firefox Mobile"
            },
            "note": {
                "en": "Uses Gecko for its web browser engine."
            },
            "links": {
                "versions": ["129", "764"],
                "history-current": "1007",
                "history": ["1007"]
            }
        },{
            "id": "8",
            "slug": "ie-phone",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie-phone.png",
            "name": {
                "en": "IE Phone"
            },
            "note": null,
            "links": {
                "versions": ["130", "765"],
                "history-current": "1008",
                "history": ["1008"]
            }
        },{
            "id": "9",
            "slug": "opera-mobile",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/opera-mobile.png",
            "name": {
                "en": "Opera Mobile"
            },
            "note": null,
            "links": {
                "versions": ["131", "767"],
                "history-current": "1009",
                "history": ["1009"]
            }
        },{
            "id": "10",
            "slug": "safari-mobile",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/safari-mobile.png",
            "name": {
                "en": "Safari Mobile"
            },
            "note": null,
            "links": {
                "versions": ["132", "768"],
                "history-current": "1010",
                "history": ["1010"]
            }
        }],
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        },
        "meta": {
            "pagination": {
                "browsers": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/browsers?page=2&per_page=10",
                    "pages": 2,
                    "per_page": 10,
                    "total": 14,
                }
            }
        }
    }

Retrieve by ID
**************

To request a single **browser**:

.. code-block:: http

    GET /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
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
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

Retrieve by Slug
****************

To request a **browser** by slug:

.. code-block:: http

    GET /browsers?slug=firefox HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": [{
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
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            }
        }],
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

Create
******

Creating **browser** instances require authentication with create privileges.
To create a new **browser** instance, ``POST`` a representation with at least
the required parameters.  Some items (such as the ``id`` attribute and the
``history-current`` link) will be picked by the server, and will be ignored if
included.

Here's an example of creating a **browser** instance:

.. code-block:: http

    POST /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "slug": "amazon-silk-mobile",
            "name": {
                "en": "Amazon Silk Mobile"
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/browsers/15

.. code-block:: json

    {
        "browsers": {
            "id": "15",
            "slug": "amazon-silk-mobile",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/amazon-silk-mobile.png",
            "name": {
                "en": "Amazon Silk Mobile"
            },
            "note": null,
            "links": {
                "versions": [],
                "history-current": "1027",
                "history": ["1027"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

This, and other methods that change resources, will create a new changeset_,
and associate the new historical-browsers_ with that changeset_.  To assign to an
existing changeset, add it to the URI:

.. code-block:: http

    POST /browsers?changeset=176 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "slug": "amazon-silk-mobile",
            "name": {
                "en": "Amazon Silk Mobile"
            }
        }
    }

Update
******

Updating a **browser** instance require authentication with create privileges.
Some items (such as the ``id`` attribute and ``history`` links) can not be
changed, and will be ignored if included.  A successful update will return a
``200 OK``, add a new ID to the ``history`` links list, and update the
``history-current`` link.

To update a **browser**:

.. code-block:: http

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

.. code-block:: json

    {
        "browsers": {
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "IE"
            },
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "IE"
            },
            "note": null,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1033",
                "history": ["1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

Partial Update
**************

An update can just update some fields:

.. code-block:: http

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

.. code-block:: json

    {
        "browsers": {
            "name": {
                "en": "M$ Internet Exploder 💩"
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "M$ Internet Exploder 💩"
            },
            "note": null,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1034",
                "history": ["1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

To change just the versions_ order:

.. code-block:: http

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

.. code-block:: json

    {
        "browsers": {
            "links": {
                "versions": ["178", "167", "125"]
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "M$ Internet Exploder 💩"
            },
            "note": null,
            "links": {
                "versions": ["178", "167", "125"],
                "history-current": "1035",
                "history": ["1035", "1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

Reverting to a previous instance
********************************

To revert to an earlier instance, set the ``history-current`` link to a
previous value.  This resets the content and creates a new
historical-browsers_ object:

.. code-block:: http

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

.. code-block:: json

    {
        "browsers": {
            "links": {
                "history-current": "1003"
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "id": "3",
            "slug": "ie",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "Internet Explorer"
            },
            "note": none,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1036",
                "history": ["1036", "1035", "1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }

Deletion
********

To delete a **browser**:

.. code-block:: http

    DELETE /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

A successful response has no body:

.. code-block:: http

    HTTP/1.1 204 No Content

Reverting a deletion
********************

To revert a deletion:

.. code-block:: http

    PUT /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browsers": {
            "id": "2",
            "slug": "firefox",
            "icon": "https://compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en": "Firefox"
            },
            "note": null,
            "links": {
                "versions": ["124"],
                "history-current": "1104",
                "history": ["1104", "1103", "1002"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/versions/{browsers.versions}",
                "type": "versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history-current}",
                "type": "historical-browsers"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{browsers.history}",
                "type": "historical-browsers"
            }
        }
    }


Versions
--------

A **version** is a specific release of a Browser.

The **versions** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **version** *(write-once)* - Version of browser, or null
      if unknown (for example, to document support for features in early HTML)
    - **release-day** - Day that browser was released in `ISO 8601`_ format, or
      null if unknown.
    - **retirement-day** - Approximate day the browser was "retired" (stopped
      being a current browser), in `ISO 8601`_ format, or null if unknown.
    - **status** - One of
      ``retired`` (old version, no longer the preferred download for any
      platform),
      ``retired-beta`` (old beta version, replaced
      by a new beta or release),
      ``current`` (current version, the preferred download or update for
      users),
      ``beta`` (a release candidate suggested for early adopters or testers),
      ``future`` (a planned future release).
    - **release-notes-uri** *(localized)* - URI of release notes for this
      version, or null if none.
    - **note** *(localized)* - Engine, OS, etc. information, or null
* **links**
    - **browser** - The related **browser**
    - **version-features** *(many)* - Associated **version-features**,
      in ID order.  Changes are ignored; work on the
      **version-features** to add, change, or remove.
    - **history-current** *(one)* - Current **browsers-versions-history**.
      Set to a value from **history** to revert to that version.
    - **history** *(many)* - Associated **historical-versions**, in time
      order (most recent first).  Changes are ignored.

To get a single **version**:

.. code-block:: http

    GET /versions/123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "versions": {
            "id": "123",
            "version": "1.0.154",
            "release-day": "2008-12-11",
            "retirement-day": "2009-05-24",
            "status": "retired",
            "release-notes-uri": null,
            "note": null,
            "links": {
                "browser": "1",
                "version-features": ["1125", "1126", "1127", "1128", "1129"],
                "history-current": "567",
                "history": ["567"]
            }
        },
        "links": {
            "versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{versions.browser}",
                "type": "browsers"
            },
            "versions.version-features": {
                "href": "https://api.compat.mozilla.org/version-features/{versions.features}",
                "type": "version-features"
            },
            "versions.history-current": {
                "href": "https://api.compat.mozilla.org/historical-versions/{versions.history-current}",
                "type": "historical-versions"
            },
            "versions.history": {
                "href": "https://api.compat.mozilla.org/historical-versions/{versions.history}",
                "type": "historical-versions"
            }
        }
    }

Features
--------
A **feature** is a web technology.  This could be a precise technology, such
as the value ``cover`` for the CSS ``background-size`` property.  It could be
a heirarchical group of related technologies, such as the CSS
``background-size`` property or the set of all CSS properties.  Some features
correspond to a page on MDN_, which will display the list of specifications
and a browser compatability table of the sub-features.

The **features** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **mdn-path** - The path to the page on MDN that this feature was
      first scraped from.  May be used in UX or for debugging import scripts.
    - **experimental** - True if a feature is considered experimental, such as
      being non-standard or part of an non-ratified spec.
    - **standardized** - True if a feature is described in a standards-track
      spec, regardless of the spec's status.
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

* **links**
    - **specification-sections** *(many)* - Associated specification-sections_.
      Order can be changed by the user.
    - **version-features** *(many)* - Associated version-features_,
      Order is in ID order, changes are ignored.
    - **parent** *(one or null)* - The feature one level up, or null
      if top-level.  Can be changed by user.
    - **ancestors** *(many)* - The features that form the path to the top of
      the tree, including this one, in bread-crumb order (top to self).  Can
      not be changed by user - set the **parent** instead.
    - **siblings** *(many)* - The features with the same parent, including
      including this one, in display order.  Can be re-ordered by the user.
    - **children** *(many)* - The features that have this feature as parent, in
      display order.  Can be an empty list, for "leaf" features.  Can be
      re-ordered by the user.
    - **descendants** *(many)* - The features in the local tree for this
      feature. including this one, in tree order.  Can not be changed by the
      user - set the **parent** on the child feature instead.
    - **history-current** *(one)* - Current historical-features_.  User can
      set to a valid **history** to revert to that version.
    - **history** *(many)* - Associated historical-features_, in time order
      (most recent first).  Changes are ignored.


To get a specific **feature** (in this case, a leaf feature with a canonical name):

.. code-block:: http

    GET /features/276 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "features": {
            "id": "276",
            "slug": "css-property-background-size-value-contain",
            "experimental": false,
            "standardized": true,
            "stable": true,
            "obsolete": false,
            "name": "background-size: contain"},
            "links": {
                "specification-sections": ["485"],
                "version-features": ["1125", "1212", "1536"],
                "parent": "173",
                "ancestors": ["2", "12", "173", "276"],
                "siblings": ["275", "276", "277"],
                "children": [],
                "descendants": ["276"],
                "history-current": "456",
                "history": ["456"]
            }
        },
        "links": {
            "features.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{features.specification-sections}",
                "type": "specification-sections"
            },
            "feature.parent": {
                "href": "https://api.compat.mozilla.org/features/{feature.parent}",
                "type": "features"
            },
            "features.ancestors": {
                "href": "https://api.compat.mozilla.org/features/{feature.ancestors}",
                "type": "features"
            },
            "features.siblings": {
                "href": "https://api.compat.mozilla.org/features/{feature.siblings}",
                "type": "features"
            },
            "features.children": {
                "href": "https://api.compat.mozilla.org/features/{feature.children}",
                "type": "features"
            },
            "features.descendants": {
                "href": "https://api.compat.mozilla.org/features/{feature.descendants}",
                "type": "features"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history-current}",
                "type": "historical-features"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history}",
                "type": "historical-features"
            }
        }
    }

Here's an example of a branch feature with a translated name (the parent of the
previous example):

.. code-block:: http

    GET /features/173 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "features": {
            "id": "173",
            "slug": "css-property-background",
            "experimental": false,
            "standardized": true,
            "stable": true,
            "obsolete": false,
            "name": {
                "en": "CSS <code>background</code> property"
            },
            "links": {
                "specification-sections": [],
                "version-features": [],
                "parent": ["12"],
                "ancestors": ["2", "12", "173"]
                "siblings": ["167", "168", "169", "170", "171", "172", "173", "174", "175"],
                "children": ["275", "276", "277"],
                "descendants": ["173", "275", "276", "277"],
                "history-current": "395",
                "history": ["395"]
            }
        },
        "links": {
            "features.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{features.specification-sections}",
                "type": "specification-sections"
            },
            "feature.parent": {
                "href": "https://api.compat.mozilla.org/features/{feature.parent}",
                "type": "features"
            },
            "features.ancestors": {
                "href": "https://api.compat.mozilla.org/features/{feature.ancestors}",
                "type": "features"
            },
            "features.siblings": {
                "href": "https://api.compat.mozilla.org/features/{feature.siblings}",
                "type": "features"
            },
            "features.children": {
                "href": "https://api.compat.mozilla.org/features/{feature.children}",
                "type": "features"
            },
            "features.descendants": {
                "href": "https://api.compat.mozilla.org/features/{feature.descendants}",
                "type": "features"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history-current}",
                "type": "historical-features"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history}",
                "type": "historical-features"
            }
        }
    }

Browser Version Features
------------------------

A **version-feature** is an assertion of the feature support for a
particular version of a browser.

The **version-feature** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **support** - Assertion of support of the version_ for the
      feature_, one of ``"yes"``, ``"no"``, ``"prefixed"``, ``"partial"``,
      ``"unknown"``, or ``"never"``
    - **prefix** - Prefix needed, if support is "prefixed"
    - **note** *(localized)* - Short note on support, designed for inline
      display, max 20 characters
    - **footnote** *(localized)* - Long note on support, designed for
      display after a compatibility table, MDN wiki format
* **links**
    - **version** *(one)* - The associated version_.  Can
      be changed by the user.
    - **feature** *(one)* - The associated feature_.  Can be changed by
      the user.
    - **history-current** *(one)* - Current
      historical-version-features_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated historical-version-features_
      in time order (most recent first).  Changes are ignored.


To get a single **version-feature**:

.. code-block:: http

    GET /version-features/1123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "version-features": {
            "id": "1123",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "version": "123",
                "feature": "276",
                "history-current": "2567",
                "history": ["2567"]
            }
        },
        "links": {
            "version-features.version": {
                "href": "https://api.compat.mozilla.org/versions/{version-features.version}",
                "type": "versions"
            },
            "version-features.feature": {
                "href": "https://api.compat.mozilla.org/browsers/{version-features.feature}",
                "type": "features"
            },
            "version-features.history-current": {
                "href": "https://api.compat.mozilla.org/historical-version-features/{version-features.history-current}",
                "type": "historical-version-features"
            },
            "version-features.history": {
                "href": "https://api.compat.mozilla.org/historical-version-features/{version-features.history}",
                "type": "historical-version-features"
            }
        }
    }

Specifications
--------------

A **specification** is a standards document that specifies a web technology.

The **specification** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **mdn-key** - The key for the KumaScript macros SpecName_ and Spec2_
      used as a data source.
    - **name** *(localized)* - Specification name
    - **uri** *(localized)* - Specification URI, without subpath and anchor
* **links**
    - **specification-sections** *(many)* - Associated specification-sections_.
      The order can be changed by the user.
    - **specification-status** *(one)* - Associated specification-status_.
      Can be changed by the user.

To get a single **specification**:

.. code-block:: http

    GET /specifications/273 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "specifications": {
            "id": "273",
            "mdn-key": "CSS1",
            "name": {
                "en": "Cascading Style Sheets, level 1",
                "fr": "Les feuilles de style en cascade, niveau 1"
            },
            "uri": {
                "en": "http://www.w3.org/TR/CSS1/",
                "fr": "http://www.yoyodesign.org/doc/w3c/css1/index.html"
            },
            "links": {
                "specification-sections": ["792", "793"]
                "specification-status": "23"
            }
        },
        "links": {
            "specifications.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{specifications.specification-sections}",
                "type": "specification-sections"
            },
            "specifications.specification-status": {
                "href": "https://api.compat.mozilla.org/specification-statuses/{specifications.specification-status}",
                "type": "specification-statuses"
            }
        }
    }

Specification Sections
----------------------

A **specification-section** refers to a specific area of a specification_
document.

The **specification-section** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **name** *(localized)* - Section name
    - **subpath** *(localized)* - A subpage (possibly with an #anchor) to get
      to the subsection in the doc.  Can be empty string.
    - **note** *(localized)* - Notes for this section
* **links**
    - **specification** *(one)* - The specification_.  Can be changed by
      the user.
    - **features** *(many)* - The associated features_.  In ID order,
      changes are ignored.

To get a single **specification-section**:

.. code-block:: http

    GET /specification-sections/792 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "specification-sections": {
            "id": "792",
            "name": {
                "en": "'display'"
            },
            "subpath": {
                "en": "#display"
            },
            "note": {
                "en": "Basic values: <code>none<\/code>, <code>block<\/code>, <code>inline<\/code>, and <code>list-item<\/code>."
            },
            "links": {
                "specification": "273",
                "features": ["275", "276", "277"],
            }
        },
        "links": {
            "specification-sections.specification": {
                "href": "https://api.compat.mozilla.org/specifications/{specification-sections.specification}",
                "type": "specifications"
            },
            "specification-sections.features": {
                "href": "https://api.compat.mozilla.org/specification-sections/{specification-sections.features}",
                "type": "features"
            }
        }
    }

Specification Statuses
----------------------

A **specification-status** refers to the status of a specification_
document.

The **specification-status** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **mdn-key** - The value for this status in the KumaScript macro Spec2_
    - **name** *(localized)* - Status name
* **links**
    - **specifications** *(many)* - Associated specifications_.  In ID order,
      changes are ignored.

To get a single **specification-status**:

.. code-block:: http

    GET /specification-statuses/49 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "specification-statuses": {
            "id": "49",
            "mdn-key": "REC",
            "name": {
                "en": "Recommendation",
                "jp": "勧告"
            },
            "links": {
                "specifications": ["84", "85", "272", "273", "274", "576"]
            }
        },
        "links": {
            "specification-statuses.specifications": {
                "href": "https://api.compat.mozilla.org/specifications/{specification-statuses.specifications}",
                "type": "specifications"
            }
        }
    }

.. _version-features: `Browser Version Features`_
.. _version: `Versions`_
.. _feature: Features_
.. _specification: Specifications_
.. _specification-sections: `Specification Sections`_
.. _specification-status: `Specification Statuses`_

.. _changeset: change-control.html#changesets

.. _historical-browsers: history.html#historical-browsers
.. _historical-version-features: history.html#historical-version-features
.. _historical-features: history.html#historical-features

.. _non-linguistic: http://www.w3.org/International/questions/qa-no-language#nonlinguistic
.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
.. _MDN: https://developer.mozilla.org
.. _SpecName: https://developer.mozilla.org/en-US/docs/Template:SpecName
.. _Spec2: https://developer.mozilla.org/en-US/docs/Template:Spec2
