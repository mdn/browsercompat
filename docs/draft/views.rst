Views
=====

A **View** is a combination of resources for a particular presentation.  It is
suitable for anonymous viewing of content.

It is possible that views are unnecessary, and could be constructed by
supporting optional parts of the JSON API spec, such as `Inclusion of Linked
Resources`_.  These views are written as if they are aliases for a
fully-fleshed implementation of JSON API.

View a Feature Set
------------------

This view collects the data for a feature-set_, including the related
resources needed to display it on MDN.

Here is a simple example, the view for the HTML element address_:

.. code-block:: http

    GET /views/view-by-feature-set/html-address HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

A sample response is:

.. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "feature-sets": {
            "id": "816"
            "slug": "html-element-address",
            "kuma-path": "en-US/docs/Web/HTML/Element/address",
            "canonical": true,
            "name": {
                "zxx": "address"
            },
            "links": {
                "features": ["191"],
                "specification-sections": ["746", "421", "70"],
                "parent": "800",
                "ancestors": ["800", "816"],
                "siblings": ["814", "815", "816", "817", "818"],
                "children": [],
                "decendants": [],
                "history-current": "216",
                "history": ["216"]
            }
        },
        "linked": {
            "features": [
                {
                    "id": "191",
                    "slug": "html-address",
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
                        "features": [],
                        "feature-sets": ["816"]
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
                        "features": [],
                        "feature-sets": ["816"]
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
                        "features": [],
                        "feature-sets": ["816"]
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
                    "kuma-key": "Living",
                    "name": {
                        "en": "Living Standard",
                    },
                    "links": {
                        "specifications": ["62"]
                    }
                }, {
                    "id": "49",
                    "kuma-key": "REC",
                    "name": {
                        "en": "Recommendation",
                        "jp": "勧告"
                    },
                    "links": {
                        "specifications": ["84", "85", "272", "273", "274", "576"]
                    }
                }, {
                    "id": "52",
                    "kuma-key": "CR",
                    "name": {
                        "en": "Candidate Recommendation",
                        "ja": "勧告候補",
                    },
                    "links": {
                        "specifications": ["83", "113", "114", "115"]
                    }
                }
            ],
            "browser-version-features": [
                {
                    "id": "358",
                    "support": "yes",
                    "prefix": null,
                    "note": null,
                    "footnote": null,
                    "links": {
                        "browser-version": "758",
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
                        "browser-version": "759",
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
                        "browser-version": "760",
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
                        "browser-version": "761",
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
                        "browser-version": "762",
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
                        "browser-version": "762",
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
                        "browser-version": "763",
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
                        "browser-version": "764",
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
                        "browser-version": "765",
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
                        "browser-version": "766",
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
                        "browser-version": "767",
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
                        "browser-version": "768",
                        "feature": "191",
                        "history-current": "3577",
                        "history": ["3577"]
                    }
                }
            ],
            "browser-versions": [
                {
                    "id": "758",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "release-notes-uri": null,
                    "links": {
                        "browser": "1",
                        "browser-version-features": ["158", "258", "358", "458"],
                        "history-current": "1567",
                        "history": ["1567"]
                    }
                }, {
                    "id": "759",
                    "version": "1.0",
                    "engine-version": "1.7",
                    "release-day": "2004-12-09",
                    "retirement-day": "2005-02-24",
                    "status": "retired",
                    "links": {
                        "browser": "2",
                        "browser-version-features": ["159", "259", "359", "459"],
                        "history-current": "1568",
                        "history": ["1568"]
                    }
                }, {
                    "id": "760",
                    "version": "1.0",
                    "engine-version": null,
                    "release-day": "1995-08-16",
                    "retirement-day": null,
                    "status": "retired",
                    "links": {
                        "browser": "3",
                        "browser-version-features": ["160", "260", "360", "460"],
                        "history-current": "1569",
                        "history": ["1569"]
                    }
                }, {
                    "id": "761",
                    "version": "5.12",
                    "engine-version": null,
                    "release-day": "2001-06-27",
                    "retirement-day": null,
                    "status": "retired",
                    "links": {
                        "browser": "4",
                        "browser-version-features": ["161", "261", "361", "461"],
                        "history-current": "1570",
                        "history": ["1570"]
                    }
                }, {
                    "id": "762",
                    "version": "1.0",
                    "engine-version": null,
                    "release-day": "2003-06-23",
                    "retirement-day": null,
                    "status": "retired",
                    "links": {
                        "browser": "5",
                        "browser-version-features": ["162", "262", "362", "462"],
                        "history-current": "1571",
                        "history": ["1571"]
                    }
                }, {
                    "id": "763",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "links": {
                        "browser": "6",
                        "browser-version-features": ["163", "263", "363", "463"],
                        "history-current": "1572",
                        "history": ["1572"]
                    }
                }, {
                    "id": "764",
                    "version": "1.0",
                    "engine-version": "1.7",
                    "release-day": null,
                    "retirement-day": null,
                    "status": "retired",
                    "links": {
                        "browser": "7",
                        "browser-version-features": ["164", "264", "364", "464"],
                        "history-current": "1574",
                        "history": ["1574"]
                    }
                }, {
                    "id": "765",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "links": {
                        "browser": "8",
                        "browser-version-features": ["165", "265", "365", "465"],
                        "history-current": "1575",
                        "history": ["1575"]
                    }
                }, {
                    "id": "766",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "links": {
                        "browser": "11",
                        "browser-version-features": ["166", "266", "366", "466"],
                        "history-current": "1576",
                        "history": ["1576"]
                    }
                }, {
                    "id": "767",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "links": {
                        "browser": "9",
                        "browser-version-features": ["167", "267", "367", "467"],
                        "history-current": "1577",
                        "history": ["1577"]
                    }
                }, {
                    "id": "768",
                    "version": null,
                    "engine-version": null,
                    "release-day": null,
                    "retirement-day": null,
                    "status": "current",
                    "links": {
                        "browser": "10",
                        "browser-version-features": ["168", "268", "368", "468"],
                        "history-current": "1578",
                        "history": ["1578"]
                    }
                }
            ]
            "browsers": [
                {
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
                },{
                    "id": "11",
                    "slug": "opera-mini",
                    "environment": "mobile",
                    "icon": "//compat.cdn.mozilla.net/media/img/browsers/opera-mini.png",
                    "name": {
                        "en": "Opera Mini"
                    },
                    "engine": null,
                    "links": {
                        "versions": ["131", "766"],
                        "history-current": "1019",
                        "history": ["1019"]
                    }
                }
            ]
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
            },
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
            },
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
            },
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
            },
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
            "compat-table-important": {
                "browsers": ["1", "2", "3", "4", "5", "6", "7", "8", "11", "9", "10"],
                "browser-version-features": {
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
    3. For each id in feature-sets.links.specification-sections (``["746", "421", "70"]``):
        * Add the first column: a link to specifications.uri.(lang or en) +
          specifications-sections.subpath.(lang or en), with link text
          specifications.name.(lang or en), with title based on
          specification-sections.name.(lang or en) or feature.name.(lang or en).
        * Add the second column: A span with class
          "spec-" + specification-statuses.kuma-key, and the text
          specification-statuses.name.(lang or en).
        * Add the third column:
          specification-statuses.notes.(lang or en), or empty string
    4. Close the table, and add an edit button.
3. Create the Browser Compatibility section:
    1. Add The "Browser compatibility" header
    2. Create two HTML tables, one for Desktop browsers, one for Mobile browsers
    3. For each browser id in meta.compat-table-important, add a column with
       the translated browser name.  If the engine has a name, add it in
       parenthesis
    4. For each feature in feature-sets.features:
        * Add the first column: the feature name.  If feature.canonical,
          use the ``zxx`` translation of feature.name wrapped in ``<code>``.
          Otherwise, use the best translation of feature.name, in a
          ``lang=(lang)`` block.
        * For each browser id in meta.compat-table-important:
            - Get the important browser-version-feature IDs from
              meta.compat-table-important.browser-version-features.<``feature ID``>.<``browser ID``>
            - If null, then display "?"
            - If just one, display "<``version``> (<``engine version``>)",
              "<``version``>", or "<``support``>", depending on the defined attributes
            - If multiple, display as subcells
            - Add prefixes, notes, and footnotes links as appropriate
    5. Close each table, add an edit button
    6. Add footnotes for displayed browser-version-features

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
version 1, you'll have to create the browser-version_ for that version,
then add the browser-version-feature_ for the support.

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
            "target-resource": "feature-sets",
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
            "target-resource": "feature-sets",
            "target-resource-id": "816",
            "links": {
                "user": "42",
                "browsers-history": [],
                "browser-versions-history": [],
                "features-history": [],
                "feature-sets-history": [],
                "browser-version-features-history": []
            }
        },
        "links": {
            "changesets.user": {
                "href": "https://api.compat.mozilla.org/users/{changesets.user}",
                "type": "users"
            },
            "changesets.browsers-history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{changesets.browsers-history}",
                "type": "browsers-history"
            },
            "changesets.browser-versions-history": {
                "href": "https://api.compat.mozilla.org/browser-versions-history/{changesets.browser-versions-history}",
                "type": "browser-versions-history"
            },
            "changesets.features-history": {
                "href": "https://api.compat.mozilla.org/features-history/{changesets.features-history}",
                "type": "features-history"
            },
            "changesets.feature-sets-history": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{changesets.feature-sets-history}",
                "type": "feature-sets-history"
            },
            "changesets.browser-version-features-history": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{changesets.browser-version-features-history}",
                "type": "browser-version-features-history"
            }
        }
    }

Next, use the changeset_ ID when creating the browser-version_:

.. code-block:: http

    POST /browser-versions/?changeset=5284 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browser-versions": {
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
    Location: https://api.compat.mozilla.org/browser-versions/4477

.. code-block:: json

    {
        "browser-versions": {
            "id": "4477",
            "version": "1",
            "engine-version": null,
            "release-day": null,
            "retirement-day": null,
            "status": "retired",
            "release-notes-uri": null,
            "links": {
                "browser": "1",
                "browser-version-features": [],
                "history-current": "3052",
                "history": ["3052"]
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

Finally, create the browser-version-feature_:

.. code-block:: http

    POST /browser-version-features/?changeset=5284 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

.. code-block:: json

    {
        "browser-version-features": {
            "support": "yes",
            "links": {
                "browser-version": "4477",
                "feature": "191"
            }
        }
    }

A sample response is:

.. code-block:: http

    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/browser-version-features/8219

.. code-block:: json

    {
        "browser-version-features": {
            "id": "8219",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "browser-version": "4477",
                "feature": "191",
                "history-current": "7164",
                "history": ["7164"]
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

The browser-versions-history_ and browser-version-features-history_
resources will both refer to changeset_ 5284, and this changeset_ is
linked to feature-set_ 816, despite the fact that no changes were made
to the feature-set_.  This will facilitate displaying a history of
the compatibility tables, for the purpose of reviewing changes and reverting
vandalism.

.. _browser-version: resources.html#browser-versions
.. _browser-version-feature: resources.html#browser-versions-feature
.. _feature-set: resources.html#feature-sets

.. _changeset: change-control#changeset

.. _browser-versions-history: history.html#browser-versions-history
.. _browser-version-features-history: history.html#browser-version-features-history

.. _address: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address
.. _`Inclusion of Linked Resources`: http://jsonapi.org/format/#fetching-includes
.. _`"caniuse" table layout`: https://wiki.mozilla.org/MDN/Development/CompatibilityTables/Data_Requirements#1._CanIUse_table_layout

