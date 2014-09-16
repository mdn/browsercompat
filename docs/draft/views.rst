Views
=====

A **View** is a combination of resources for a particular presentation.  It is
suitable for anonymous viewing of content.

It is possible that views are unnecessary, and could be constructed by
supporting optional parts of the JSON API spec, such as `Inclusion of Linked
Resources`_.  These views are written as if they are aliases for a
fully-fleshed implementation of JSON API.

View a Feature
--------------

This view collects the data for a feature_, including the related
resources needed to display it on MDN.

Here is a simple example, the view for the HTML element address_:

.. code-block:: http

    GET /views/view-by-feature/html-element-address HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "features": {
            "id": "816"
            "slug": "html-element-address",
            "experimental": false,
            "standardized": true,
            "stable": true,
            "obsolete": false,
            "mdn-path": "en-US/docs/Web/HTML/Element/address",
            "name": "address",
            "links": {
                "specification-sections": ["746", "421", "70"],
                "supports": [],
                "parent": "800",
                "ancestors": ["800", "816"],
                "siblings": ["814", "815", "816", "817", "818"],
                "children": ["191"],
                "descendants": ["816", "191"],
                "history-current": "216",
                "history": ["216"]
            }
        },
        "linked": {
            "features": [
                {
                    "id": "191",
                    "slug": "html-address",
                    "experimental": false,
                    "standardized": true,
                    "stable": true,
                    "obsolete": false,
                    "name": {
                        "en": "Basic support"
                    },
                    "links": {
                        "specification-sections": [],
                        "supports": [
                            "358", "359", "360", "361", "362", "363", "364",
                            "365", "366", "367", "368"],
                        "parent": "816",
                        "ancestors": ["800", "816", "191"],
                        "siblings": ["191"],
                        "children": [],
                        "descendants": ["191"],
                        "history-current": "395",
                        "history": ["395"]
                    }
                }
            ],
            "specification-sections": [
                {
                    "id": "746",
                    "name": {
                        "en": "The address element"
                    },
                    "subpath": {
                        "en": "sections.html#the-address-element"
                    },
                    "notes": null,
                    "links": {
                        "specification": "273",
                        "features": ["816"],
                    }
                },{
                    "id": "421",
                    "name": {
                        "en": "The address element"
                    },
                    "subpath": {
                        "en": "sections.html#the-address-element"
                    },
                    "notes": null,
                    "links": {
                        "specification": "114",
                        "features": ["816"],
                    }
                },{
                    "id": "70",
                    "name": {
                        "en": "The ADDRESS element"
                    },
                    "subpath": {
                        "en": "struct/global.html#h-7.5.6"
                    },
                    "notes": null,
                    "links": {
                        "specification": "576",
                        "features": ["816"],
                    }
                }
            ],
            "specifications": [
                {
                    "id": "62",
                    "kumu-key": "HTML WHATWG",
                    "name": {
                        "en": "WHATWG HTML Living Standard",
                    },
                    "uri": {
                        "en": "http://www.whatwg.org/specs/web-apps/current-work/multipage/",
                    },
                    "links": {
                        "specification-sections": ["745", "746", "747"]
                        "specification-status": "23"
                    }
                },{
                    "id": "114",
                    "kumu-key": "HTML5 W3C",
                    "name": {
                        "en": "HTML5",
                    },
                    "uri": {
                        "en": "http://www.w3.org/TR/html5/",
                    },
                    "links": {
                        "specification-sections": ["420", "421", "422"]
                        "specification-status": "52"
                    }
                },{
                    "id": "576",
                    "kumu-key": "HTML4.01",
                    "name": {
                        "en": "HTML 4.01 Specification",
                    },
                    "uri": {
                        "en": "http://www.w3.org/TR/html401/",
                    },
                    "links": {
                        "specification-sections": ["69", "70", "71"]
                        "specification-status": "49"
                    }
                }
            ],
            "specification-statuses": [
                {
                    "id": "23",
                    "mdn-key": "Living",
                    "name": {
                        "en": "Living Standard",
                    },
                    "links": {
                        "specifications": ["62"]
                    }
                }, {
                    "id": "49",
                    "mdn-key": "REC",
                    "name": {
                        "en": "Recommendation",
                        "jp": "勧告"
                    },
                    "links": {
                        "specifications": ["84", "85", "272", "273", "274", "576"]
                    }
                }, {
                    "id": "52",
                    "mdn-key": "CR",
                    "name": {
                        "en": "Candidate Recommendation",
                        "ja": "勧告候補",
                    },
                    "links": {
                        "specifications": ["83", "113", "114", "115"]
                    }
                }
            ],
            "supports": [
                {
                    "id": "358",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "758",
                        "feature": "191",
                        "history-current": "3567",
                        "history": ["3567"]
                    }
                }, {
                    "id": "359",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "759",
                        "feature": "191",
                        "history-current": "3568",
                        "history": ["3568"]
                    }
                }, {
                    "id": "360",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "760",
                        "feature": "191",
                        "history-current": "3569",
                        "history": ["3569"]
                    }
                }, {
                    "id": "361",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "761",
                        "feature": "191",
                        "history-current": "3570",
                        "history": ["3570"]
                    }
                }, {
                    "id": "362",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "762",
                        "feature": "191",
                        "history-current": "3571",
                        "history": ["3571"]
                    }
                }, {
                    "id": "362",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "762",
                        "feature": "191",
                        "history-current": "3571",
                        "history": ["3571"]
                    }
                }, {
                    "id": "363",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "763",
                        "feature": "191",
                        "history-current": "3572",
                        "history": ["3572"]
                    }
                }, {
                    "id": "364",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "764",
                        "feature": "191",
                        "history-current": "3573",
                        "history": ["3573"]
                    }
                }, {
                    "id": "365",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "765",
                        "feature": "191",
                        "history-current": "3574",
                        "history": ["3574"]
                    }
                }, {
                    "id": "366",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "766",
                        "feature": "191",
                        "history-current": "3575",
                        "history": ["3575"]
                    }
                }, {
                    "id": "367",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "767",
                        "feature": "191",
                        "history-current": "3576",
                        "history": ["3576"]
                    }
                }, {
                    "id": "368",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "version": "768",
                        "feature": "191",
                        "history-current": "3577",
                        "history": ["3577"]
                    }
                }
            ],
            "versions": [
                {
                    "id": "758",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "1",
                        "supports": ["158", "258", "358", "458"],
                        "history-current": "1567",
                        "history": ["1567"]
                    }
                }, {
                    "id": "759",
                    "version": "1.0",
                    "release-day": "2004-12-09",
                    "retirement-day": "2005-02-24",
                    "status": "retired",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "2",
                        "supports": ["159", "259", "359", "459"],
                        "history-current": "1568",
                        "history": ["1568"]
                    }
                }, {
                    "id": "760",
                    "version": "1.0",
                    "release-day": "1995-08-16",
                    "retirement-day": null,
                    "status": "retired",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "3",
                        "supports": ["160", "260", "360", "460"],
                        "history-current": "1569",
                        "history": ["1569"]
                    }
                }, {
                    "id": "761",
                    "version": "5.12",
                    "release-day": "2001-06-27",
                    "retirement-day": null,
                    "status": "retired",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "4",
                        "supports": ["161", "261", "361", "461"],
                        "history-current": "1570",
                        "history": ["1570"]
                    }
                }, {
                    "id": "762",
                    "version": "1.0",
                    "release-day": "2003-06-23",
                    "retirement-day": null,
                    "status": "retired",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "5",
                        "supports": ["162", "262", "362", "462"],
                        "history-current": "1571",
                        "history": ["1571"]
                    }
                }, {
                    "id": "763",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "6",
                        "supports": ["163", "263", "363", "463"],
                        "history-current": "1572",
                        "history": ["1572"]
                    }
                }, {
                    "id": "764",
                    "version": "1.0",
                    "release-day": null,
                    "retirement-day": null,
                    "status": "retired",
                    "release-notes-uri": null,
                    "note": "Uses Gecko 1.7",
                    "links": {
                        "browser": "7",
                        "supports": ["164", "264", "364", "464"],
                        "history-current": "1574",
                        "history": ["1574"]
                    }
                }, {
                    "id": "765",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "8",
                        "supports": ["165", "265", "365", "465"],
                        "history-current": "1575",
                        "history": ["1575"]
                    }
                }, {
                    "id": "766",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "11",
                        "supports": ["166", "266", "366", "466"],
                        "history-current": "1576",
                        "history": ["1576"]
                    }
                }, {
                    "id": "767",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "9",
                        "supports": ["167", "267", "367", "467"],
                        "history-current": "1577",
                        "history": ["1577"]
                    }
                }, {
                    "id": "768",
                    "version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "note": null,
                    "links": {
                        "browser": "10",
                        "supports": ["168", "268", "368", "468"],
                        "history-current": "1578",
                        "history": ["1578"]
                    }
                }
            ]
            "browsers": [
                {
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
                },{
                    "id": "11",
                    "slug": "opera-mini",
                    "icon": "https://compat.cdn.mozilla.net/media/img/browsers/opera-mini.png",
                    "name": {
                        "en": "Opera Mini"
                    },
                    "note": null,
                    "links": {
                        "versions": ["131", "766"],
                        "history-current": "1019",
                        "history": ["1019"]
                    }
                }
            ]
        },
        "links": {
            "features.features": {
                "href": "https://api.compat.mozilla.org/features/{features.features}",
                "type": "features"
            },
            "features.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{features.specification-sections}",
                "type": "specification-sections"
            },
            "features.parent": {
                "href": "https://api.compat.mozilla.org/features/{features.parent}",
                "type": "features"
            },
            "features.ancestors": {
                "href": "https://api.compat.mozilla.org/features/{features.ancestors}",
                "type": "features"
            },
            "features.siblings": {
                "href": "https://api.compat.mozilla.org/features/{features.siblings}",
                "type": "features"
            },
            "features.children": {
                "href": "https://api.compat.mozilla.org/features/{features.children}",
                "type": "features"
            },
            "features.descendants": {
                "href": "https://api.compat.mozilla.org/features/{features.descendants}",
                "type": "features"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history-current}",
                "type": "historical-features"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/historical-features/{features.history}",
                "type": "historical-features"
            },
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
            },
            "versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{versions.browser}",
                "type": "browsers"
            },
            "versions.supports": {
                "href": "https://api.compat.mozilla.org/supports/{versions.features}",
                "type": "supports"
            },
            "versions.history-current": {
                "href": "https://api.compat.mozilla.org/historical-versions/{versions.history-current}",
                "type": "historical-versions"
            },
            "versions.history": {
                "href": "https://api.compat.mozilla.org/historical-versions/{versions.history}",
                "type": "historical-versions"
            },
            "supports.version": {
                "href": "https://api.compat.mozilla.org/versions/{supports.version}",
                "type": "versions"
            },
            "supports.feature": {
                "href": "https://api.compat.mozilla.org/browsers/{supports.feature}",
                "type": "features"
            },
            "supports.history-current": {
                "href": "https://api.compat.mozilla.org/historical-supports/{supports.history-current}",
                "type": "historical-supports"
            },
            "supports.history": {
                "href": "https://api.compat.mozilla.org/historical-supports/{supports.history}",
                "type": "historical-supports"
            },
            "specifications.specification-sections": {
                "href": "https://api.compat.mozilla.org/specification-sections/{specifications.specification-sections}",
                "type": "specification-sections"
            },
            "specifications.specification-status": {
                "href": "https://api.compat.mozilla.org/specification-statuses/{specifications.specification-status}",
                "type": "specification-statuses"
            },
            "specification-sections.specification": {
                "href": "https://api.compat.mozilla.org/specifications/{specification-sections.specification}",
                "type": "specifications"
            },
            "specification-sections.features": {
                "href": "https://api.compat.mozilla.org/specification-sections/{specification-sections.features}",
                "type": "features"
            },
            "specification-statuses.specifications": {
                "href": "https://api.compat.mozilla.org/specifications/{specification-statuses.specifications}",
                "type": "specifications"
            }
        },
        "meta": {
            "compat-table": {
                "tabs": [{
                    "name": {
                        "en": "Desktop"
                    },
                    "browsers": ["1", "2", "3", "4", "5"]
                },{
                    "name": {
                        "en": "Mobile"
                    },
                    "browsers": ["6", "7", "8", "11", "9", "10"]
                }],
                "supports": {
                    "191": {
                        "1": ["358"],
                        "2": ["359"],
                        "3": ["360"],
                        "4": ["361"],
                        "5": ["362"],
                        "6": ["363"],
                        "7": ["364"],
                        "8": ["365"],
                        "11": ["366"],
                        "9": ["367"],
                        "10": ["368"]
                    }
                }
            }
        }
    }

The process for using this representation is:

1. Parse into an in-memory object store,
2. Create the "Specifications" section:
    1. Add the ``Specifications`` header
    2. Create an HTML table with a header row "Specification", "Status", "Comment"
    3. For each id in features.links.specification-sections (``["746", "421", "70"]``):
        * Add the first column: a link to specifications.uri.(lang or en) +
          specifications-sections.subpath.(lang or en), with link text
          specifications.name.(lang or en), with title based on
          specification-sections.name.(lang or en) or feature.name.(lang or en).
        * Add the second column: A span with class
          "spec-" + specification-statuses.mdn-key, and the text
          specification-statuses.name.(lang or en).
        * Add the third column:
          specification-statuses.notes.(lang or en), or empty string
    4. Close the table, and add an edit button.
3. Create the Browser Compatibility section:
    1. Add The "Browser compatibility" header
    2. For each item in meta.compat-table.tabs, create a table with the proper
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
            - Add prefixes, notes, and footnotes links as appropriate
    5. Close each table, add an edit button
    6. Add footnotes for displayed supports

This may be done by including the JSON in the page as sent over the wire,
or loaded asynchronously, with the tables built after initial page load.

This can also be used by a `"caniuse" table layout`_ by ignoring the meta
section and displaying all the included data.  This will require more
client-side processing to generate, or additional data in the ``<meta>``
section.

Updating Views with Changesets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating the page requires a sequence of requests.  For example, if a user
wants to change Chrome support for ``<address>`` from an unknown version to
version 1, you'll have to create the version_ for that version,
then add the support_ for the support.

The first step is to create a changeset_ as an authenticated user:

.. code-block:: http

    POST /changesets/ HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "changesets": {
            "target-resource": "features",
            "target-resource-id": "816"
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/changesets/5284

.. code-block:: json

    {
        "changesets": {
            "id": "5284",
            "created": "1405360263.670000",
            "modified": "1405360263.670000",
            "target-resource": "features",
            "target-resource-id": "816",
            "links": {
                "user": "42",
                "historical-browsers": [],
                "historical-versions": [],
                "historical-features": [],
                "historical-supports": []
            }
        },
        "links": {
            "changesets.user": {
                "href": "https://api.compat.mozilla.org/users/{changesets.user}",
                "type": "users"
            },
            "changesets.historical-browsers": {
                "href": "https://api.compat.mozilla.org/historical-browsers/{changesets.historical-browsers}",
                "type": "historical-browsers"
            },
            "changesets.historical-versions": {
                "href": "https://api.compat.mozilla.org/historical-versions/{changesets.historical-versions}",
                "type": "historical-versions"
            },
            "changesets.historical-features": {
                "href": "https://api.compat.mozilla.org/historical-features/{changesets.historical-features}",
                "type": "historical-features"
            },
            "changesets.historical-supports": {
                "href": "https://api.compat.mozilla.org/historical-supports/{changesets.historical-supports}",
                "type": "historical-supports"
            }
        }
    }

Next, use the changeset_ ID when creating the version_:

.. code-block:: http

    POST /versions/?changeset=5284 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "versions": {
            "version": "1",
            "status": "retired",
            "links": {
                "browser": "1",
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/versions/4477

.. code-block:: json

    {
        "versions": {
            "id": "4477",
            "version": "1",
            "release-day": null,
            "retirement-day": null,
            "status": "retired",
            "release-notes-uri": null,
            "note": null,
            "links": {
                "browser": "1",
                "supports": [],
                "history-current": "3052",
                "history": ["3052"]
            }
        },
        "links": {
            "versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{versions.browser}",
                "type": "browsers"
            },
            "versions.supports": {
                "href": "https://api.compat.mozilla.org/supports/{versions.features}",
                "type": "supports"
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

Finally, create the support_:

.. code-block:: http

    POST /supports/?changeset=5284 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "supports": {
            "support": "yes",
            "links": {
                "version": "4477",
                "feature": "191"
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/supports/8219

.. code-block:: json

    {
        "supports": {
            "id": "8219",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "version": "4477",
                "feature": "191",
                "history-current": "7164",
                "history": ["7164"]
            }
        },
        "links": {
            "supports.version": {
                "href": "https://api.compat.mozilla.org/versions/{supports.version}",
                "type": "versions"
            },
            "supports.feature": {
                "href": "https://api.compat.mozilla.org/browsers/{supports.feature}",
                "type": "features"
            },
            "supports.history-current": {
                "href": "https://api.compat.mozilla.org/historical-supports/{supports.history-current}",
                "type": "historical-supports"
            },
            "supports.history": {
                "href": "https://api.compat.mozilla.org/historical-supports/{supports.history}",
                "type": "historical-supports"
            }
        }
    }

The historical-versions_ and historical-supports_
resources will both refer to changeset_ 5284, and this changeset_ is
linked to feature_ 816, despite the fact that no changes were made
to the feature_.  This will facilitate displaying a history of
the compatibility tables, for the purpose of reviewing changes and reverting
vandalism.

.. _feature: resources.html#features
.. _support: resources.html#versions-feature
.. _version: resources.html#versions

.. _changeset: change-control#changeset

.. _historical-versions: history.html#historical-versions
.. _historical-supports: history.html#historical-supports

.. _address: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address
.. _`Inclusion of Linked Resources`: http://jsonapi.org/format/#fetching-includes
.. _`"caniuse" table layout`: https://wiki.mozilla.org/MDN/Development/CompatibilityTables/Data_Requirements#1._CanIUse_table_layout

