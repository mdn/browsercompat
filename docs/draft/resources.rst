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
    - **environment** - String, must be one of "desktop" or "mobile"
    - **icon** - Protocol-less path to representative icon
    - **name** *(localized)* - Browser name
    - **engine** *(localized)* - Browser engine, or null if not version tracked
* **links**
    - **versions** *(many)* - Associated browser-versions_, ordered roughly
      from earliest to latest.  User can change the order.
    - **history-current** *(one)* - Current browsers-history_.  Can be
      set to a value from **history** to revert changes.
    - **history** *(many)* - Associated browsers-history_ in time order
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/chrome.png",
            "name": {
                "en": "Chrome"
            },
            "engine": null,
            "links": {
                "versions": ["123", "758"],
                "history-current": "1001",
                "history": ["1001"]
            }
        },{
            "id": "2",
            "slug": "firefox",
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en": "Firefox"
            },
            "engine": {
                "en": "Gecko"
            },
            "links": {
                "versions": ["124", "759"],
                "history-current": "1002",
                "history": ["1002"]
            }
        },{
            "id": "3",
            "slug": "ie",
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "Internet Explorer"
            },
            "engine": null,
            "links": {
                "versions": ["125", "167", "178", "760"],
                "history-current": "1003",
                "history": ["1003"]
            }
        },{
            "id": "4",
            "slug": "opera",
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/opera.png",
            "name": {
                "en": "Opera"
            },
            "engine": null,
            "links": {
                "versions": ["126", "761"],
                "history-current": "1004",
                "history": ["1004"]
            }
        },{
            "id": "5",
            "slug": "safari",
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/safari.png",
            "name": {
                "en": "Safari"
            },
            "engine": {
                "en": "Webkit"
            },
            "links": {
                "versions": ["127", "762"],
                "history-current": "1005",
                "history": ["1005"]
            }
        },{
            "id": "6",
            "slug": "android",
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/android.png",
            "name": {
                "en": "Android"
            },
            "engine": null,
            "links": {
                "versions": ["128", "763"],
                "history-current": "1006",
                "history": ["1006"]
            }
        },{
            "id": "7",
            "slug": "firefox-mobile",
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox-mobile.png",
            "name": {
                "en": "Firefox Mobile"
            },
            "engine": {
                "en": "Gecko"
            },
            "links": {
                "versions": ["129", "764"],
                "history-current": "1007",
                "history": ["1007"]
            }
        },{
            "id": "8",
            "slug": "ie-phone",
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie-phone.png",
            "name": {
                "en": "IE Phone"
            },
            "engine": null,
            "links": {
                "versions": ["130", "765"],
                "history-current": "1008",
                "history": ["1008"]
            }
        },{
            "id": "9",
            "slug": "opera-mobile",
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/opera-mobile.png",
            "name": {
                "en": "Opera Mobile"
            },
            "engine": null,
            "links": {
                "versions": ["131", "767"],
                "history-current": "1009",
                "history": ["1009"]
            }
        },{
            "id": "10",
            "slug": "safari-mobile",
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/safari-mobile.png",
            "name": {
                "en": "Safari Mobile"
            },
            "engine": null,
            "links": {
                "versions": ["132", "768"],
                "history-current": "1010",
                "history": ["1010"]
            }
        }],
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en": "Firefox"
            },
            "engine": {
                "en": "Gecko"
            },
            "links": {
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }

Retrieve by Slug
****************

To request a **browser** by slug:

.. code-block:: http

    GET /browsers/firefox HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/browsers/2

.. code-block:: json

    {
        "browsers": {
            "id": "2",
            "slug": "firefox",
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en": "Firefox"
            },
            "engine": {
                "en": "Gecko"
            },
            "links": {
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
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
            "environment": "mobile",
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
            "environment": "mobile",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/amazon-silk-mobile.png",
            "name": {
                "en": "Amazon Silk Mobile"
            },
            "engine": null,
            "links": {
                "versions": [],
                "history-current": "1027",
                "history": ["1027"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }

This, and other methods that change resources, will create a new changeset_,
and associate the new browsers-history_ with that changeset_.  To assign to an
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
            "environment": "mobile",
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "IE"
            },
            "engine": null
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "IE"
            },
            "engine": null,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1033",
                "history": ["1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "M$ Internet Exploder 💩"
            },
            "engine": null,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1034",
                "history": ["1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }

To change just the browser-versions_ order:

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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "M$ Internet Exploder 💩"
            },
            "engine": null,
            "links": {
                "versions": ["178", "167", "125"],
                "history-current": "1035",
                "history": ["1035", "1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }

Reverting to a previous version
*******************************

To revert to an earlier version, set the ``history-current`` link to a
previous value.  This resets the content and creates a new
browsers-history_ object:

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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/ie.png",
            "name": {
                "en": "Internet Explorer"
            },
            "engine": null,
            "links": {
                "versions": ["125", "167", "178"],
                "history-current": "1036",
                "history": ["1036", "1035", "1034", "1033", "1003"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
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
            "environment": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en": "Firefox"
            },
            "engine": {
                "en": "Gecko"
            },
            "links": {
                "versions": ["124"],
                "history-current": "1104",
                "history": ["1104", "1103", "1002"]
            }
        },
        "links": {
            "browsers.versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            },
            "browsers.history-current": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history-current}",
                "type": "browsers-history"
            },
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }


Browser Versions
----------------

A **browser-version** is a specific release of a Browser.

The **browser-versions** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **version** *(write-once)* - Version of browser, or null
      if unknown (for example, to document support for features in early HTML)
    - **engine-version** *(write-once)* - Version of browser engine, or null
      if not tracked
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
* **links**
    - **browser** - The related **browser**
    - **browser-version-features** *(many)* - Associated **browser-version-features**,
      in ID order.  Changes are ignored; work on the
      **browser-version-features** to add, change, or remove.
    - **history-current** *(one)* - Current **browsers-versions-history**.
      Set to a value from **history** to revert to that version.
    - **history** *(many)* - Associated **browser-versions-history**, in time
      order (most recent first).  Changes are ignored.

To get a single **browser-version**:

.. code-block:: http

    GET /browser-versions/123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browser-versions": {
            "id": "123",
            "version": "1.0.154",
            "engine-version": null,
            "release-day": "2008-12-11",
            "retirement-day": "2009-05-24",
            "status": "retired",
            "release-notes-uri": null,
            "links": {
                "browser": "1",
                "browser-version-features": ["1125", "1126", "1127", "1128", "1129"],
                "history-current": "567",
                "history": ["567"]
            }
        },
        "links": {
            "browser-versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.browser}",
                "type": "browsers"
            },
            "browser-versions.browser-version-features": {
                "href": "https://api.compat.mozilla.org/browser-version-features/{browser-versions.features}",
                "type": "browser-version-features"
            },
            "browser-versions.history-current": {
                "href": "https://api.compat.mozilla.org/browser-versions-history/{browser-versions.history-current}",
                "type": "browser-versions-history"
            },
            "browser-versions.history": {
                "href": "https://api.compat.mozilla.org/browser-versions-history/{browser-versions.history}",
                "type": "browser-versions-history"
            }
        }
    }

Features
--------

A **feature** is a precise web technology, such as the value ``cover`` for the
CSS ``background-size`` property.

The **features** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **maturity** - Is the feature part of a current recommended standard?
      One of the following:
      ``standard`` (default value, feature is defined in a current standard),
      ``non-standard`` (feature was never defined in a standard or was
      explicitly removed by a current standard),
      ``experimental`` (feature is part of a standard that isn't endorsed,
      such as a working draft or on the recommendation track)
    - **canonical** - true if the **name** is a canonical name, representing
      code that a developer could use directly.  For example, ``"display: none"`` is
      the canonical name for the CSS display property with a value of none,
      while ``"Basic support"`` and
      ``"<code>none, inline</code> and <code>block</code>"``
      are non-canonical names that should be translated.
    - **name** *(localized)* - Feature name.  When **canonical** is True, the
      only translated string is in the non-linguistic_ language ``zxx``, and
      should be wrapped in a ``<code>`` block when displayed.  When
      **canonical** is false, the name will include at least an ``en``
      translation, and may include HTML markup.
* **links**
    - **feature-sets** *(many)* - Associated feature-sets_.  Ideally, a
      feature is contained in a single feature-set_ but it may be
      associated with multiple feature-sets_ during a transition
      period.  Order is in ID order, changes are ignored.
    - **specification-sections** *(many)* - Associated specification-sections_.
      Order can be changed by the user.
    - **browser-version-features** *(many)* - Associated browser-version-features_,
      Order is in ID order, changes are ignored.
    - **history-current** *(one)* - Current features-history_.  User can
      set to a valid **history** to revert to that version.
    - **history** *(many)* - Associated features-history_, in time order
      (most recent first).  Changes are ignored.

To get a specific **feature** (in this case, a canonically-named feature):

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
            "maturity": "standard",
            "canonical": true,
            "name": {
                "zxx": "background-size: contain"
            },
            "links": {
                "feature-sets": ["373"],
                "specification-sections": ["485"],
                "browser-version-features": ["1125", "1212", "1536"],
                "history-current": "456",
                "history": ["456"]
            }
        },
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "features.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{features.specification-sections}",
                "type": "specification-sections"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history-current}",
                "type": "features-history"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history}",
                "type": "features-history"
            }
        }
    }

Here's an example of a non-canonically named feature:

.. code-block:: http

    GET /features/191 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "features": {
            "id": "191",
            "slug": "html-element-address",
            "maturity": "standard",
            "canonical": false,
            "name": {
                "en": "Basic support"
            },
            "links": {
                "feature-sets": ["816"],
                "specification-sections": [],
                "browser-version-features": [
                    "358", "359", "360", "361", "362", "363", "364",
                    "365", "366", "367", "368"],
                "history-current": "395",
                "history": ["395"]
            }
        },
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "features.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{features.specification-sections}",
                "type": "specification-sections"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history-current}",
                "type": "features-history"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history}",
                "type": "features-history"
            }
        }
    }

Feature Sets
------------

A **feature-set** organizes features into a heierarchy of logical groups.  A
**feature-set** corresponds to a page on MDN_, which will display a list of
specifications and a browser compatibility table.

The **feature-sets** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **kuma-path** - The path to the page on MDN that this feature-set was
      first scraped from.  May be used in UX or for debugging import scripts.
    - **canonical** - true if the feature set has a canonical name,
      representing code that a developer could use directly.  For example,
      ``"display"`` is a canonical name for the CSS display property, and
      should not be translated, while ``"CSS"`` and ``"Flexbox Values for
      <code>display</code>"`` are non-canonical names that should be
      translated.
    - **name** *(localized)* - Feature set name.  When **canonical** is True,
      the only translated string is in the non-linguistic_ language ``zxx``,
      and should be wrapped in a ``<code>`` block when displayed.  When
      **canonical** is false, the name will include at least an ``en``
      translation, and may include HTML markup.
* **links**
    - **features** *(many)* - Associated features_.  Can be re-ordered by
      the user.
    - **specification-sections** *(many)* - Associated
      specification-sections_.  Can be re-ordered by the user.
    - **parent** *(one or null)* - The feature-set one level up, or null
      if top-level.  Can be changed by user.
    - **ancestors** *(many)* - The feature-sets that form the path to the
      top of the tree, including this one, in bread-crumb order (top to self).
      Can not be changed by user - set the **parent** instead.
    - **siblings** *(many)* - The feature-sets with the same parent,
      including including this one, in display order.  Can be re-ordered by the
      user.
    - **children** *(many)* - The feature-sets that have this
      feature-set as parent, in display order.  Can be re-ordered by the
      user.
    - **decendants** *(many)* - The feature-sets in the local tree for
      this feature-set. including this one, in tree order.  Can not be
      changed by the user - set the **parent** on the child feature-set
      instead.
    - **history-current** *(one)* - The current feature-sets-history_
    - **history** *(many)* - Associated feature-sets-history_, in time
      order (most recent first).  Can not be re-ordered by user.


To get a single **feature set** (in this case, a canonically named feature):

.. code-block:: http

    GET /features-sets/373 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "feature-sets": {
            "id": "373",
            "slug": "css-property-background-size",
            "kuma-path": "en-US/docs/Web/CSS/display",
            "canonical": true,
            "name": {
                "zxx": "background-size"
            },
            "links": {
                "features": ["275", "276", "277"],
                "specification-sections": [],
                "parent": "301",
                "ancestors": ["301", "373"],
                "siblings": ["372", "373", "374", "375"],
                "children": [],
                "decendants": [],
                "history-current": "648",
                "history": ["648"]
            }
        },
        "links": {
            "feature-sets.features": {
                "href": "https://api.compat.mozilla.org/features/{feature-sets.features}",
                "type": "features"
            },
            "feature-sets.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{feature-sets.specification-sections}",
                "type": "specfication-sections"
            },
            "feature-sets.parent": {
                "href": "https://api.compat.mozilla.org/feature-sets/{feature-sets.parent}",
                "type": "feature-sets"
            },
            "feature-sets.ancestors": {
                "href": "https://api.compat.mozilla.org/feature-sets/{feature-sets.ancestors}",
                "type": "feature-sets"
            },
            "feature-sets.siblings": {
                "href": "https://api.compat.mozilla.org/feature-sets/{feature-sets.siblings}",
                "type": "feature-sets"
            },
            "feature-sets.children": {
                "href": "https://api.compat.mozilla.org/feature-sets/{feature-sets.children}",
                "type": "feature-sets"
            },
            "feature-sets.decendants": {
                "href": "https://api.compat.mozilla.org/feature-sets/{feature-sets.decendants}",
                "type": "feature-sets"
            },
            "feature-sets.history-current": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{feature-sets.history-current}",
                "type": "feature-sets-history"
            },
            "feature-sets.history": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{feature-sets.history}",
                "type": "feature-sets-history"
            }
        }
    }

Browser Version Features
------------------------

A **browser-version-feature** is an assertion of the feature support for a
particular version of a browser.

The **browser-version-feature** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **support** - Assertion of support of the browser-version_ for the
      feature_, one of ``"yes"``, ``"no"``, ``"prefixed"``, ``"partial"``,
      ``"unknown"``, or ``"never"``
    - **prefix** - Prefix needed, if support is "prefixed"
    - **note** *(localized)* - Short note on support, designed for inline
      display, max 20 characters
    - **footnote** *(localized)* - Long note on support, designed for
      display after a compatibility table, MDN wiki format
* **links**
    - **browser-version** *(one)* - The associated browser-version_.  Can
      be changed by the user.
    - **feature** *(one)* - The associated feature_.  Can be changed by
      the user.
    - **history-current** *(one)* - Current
      browser-version-features-history_.  Can be changed to a valid
      **history** to revert to that version.
    - **history** *(many)* - Associated browser-version-features-history_
      in time order (most recent first).  Changes are ignored.


To get a single **browser-version-feature**:

.. code-block:: http

    GET /browser-version-features/1123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browser-version-features": {
            "id": "1123",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "browser-version": "123",
                "feature": "276",
                "history-current": "2567",
                "history": ["2567"]
            }
        },
        "links": {
            "browser-version-features.browser-version": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browser-version-features.browser-version}",
                "type": "browser-versions"
            },
            "browser-version-features.feature": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-version-features.feature}",
                "type": "features"
            },
            "browser-version-features.history-current": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{browser-version-features.history-current}",
                "type": "browser-version-features-history"
            },
            "browser-version-features.history": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{browser-version-features.history}",
                "type": "browser-version-features-history"
            }
        }
    }

Specifications
--------------

A **specification** is a standards document that specifies a web technology.

The **specification** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **kuma-key** - The key for the KumaScript macros SpecName_ and Spec2_
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
            "kuma-key": "CSS1",
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
    - **feature-sets** *(many)* - The associated feature-sets_.  In ID
      order, changes are ignored.

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
            "notes": {
                "en": "Basic values: <code>none<\/code>, <code>block<\/code>, <code>inline<\/code>, and <code>list-item<\/code>."
            },
            "links": {
                "specification": "273",
                "features": ["275", "276", "277"],
                "feature-sets": [],
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
    - **kuma-key** - The value for this status in the KumaScript macro Spec2_
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
            "kuma-key": "REC",
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

.. _browser-version-features: `Browser Version Features`_
.. _browser-version: `Browser Versions`_
.. _browser-versions: `Browser Versions`_
.. _feature: Features_
.. _feature-set: `Feature Sets`_
.. _feature-sets: `Feature Sets`_
.. _specification: Specifications_
.. _specification-sections: `Specification Sections`_
.. _specification-status: `Specification Statuses`_

.. _changeset: change-control.html#changesets

.. _browsers-history: history.html#browsers-history
.. _browser-version-features-history: history.html#browser-version-features-history
.. _features-history: history.html#features-history
.. _feature-sets-history: history.html#feature-sets-history

.. _non-linguistic: http://www.w3.org/International/questions/qa-no-language#nonlinguistic
.. _`ISO 8601`: http://en.wikipedia.org/wiki/ISO_8601
.. _MDN: https://developer.mozilla.org
.. _SpecName: https://developer.mozilla.org/en-US/docs/Template:SpecName
.. _Spec2: https://developer.mozilla.org/en-US/docs/Template:Spec2
