# Mozilla Web Compatibility API

**This is a draft document**

The [MDN community](http://developer.mozilla.org) maintains information about
web technologies such as HTML and CSS.  This includes information about which
specifications define the technology, and what browsers support the technology.

Browser support is shown in **Browser compatibility** tables in the source.  A
simple example is for the
[HTML element &lt;address&gt;](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address#Browser_compatibility).
A more complex example is the
[CSS property display](https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility).

There are several issues with the table-based compatibility tables, some of
which could be solved by having a database-backed representation of
compatibilty data, readable and writable from an API.

# The Entrypoints

The API will be reachable at <https://api.compat.mozilla.org>. A non-SSL
version will be reachable at <http://api.compat.mozilla.org>, and will
redirect to the SSL version.  This site is for applications that read,
create, update, and delete compatibility resources.  It includes a
browsable API to ease application development, but not full documentation.

The API supports two representations:

* `application/vnd.api+json` *(default)* - JSON mostly conforming to the
  [JSON API](http://jsonapi.org).
* `text/html` - the Django REST Framework browsable API.

The API supports user accounts with
[Persona](http://www.mozilla.org/en-US/persona/) authentication.  Persona
credentials can be exchanged for an [OAuth 2.0](http://oauth.net/2/) token
for server-side code changes.

A developer-centered website will be available at <https://compat.mozilla.org>.
A non-SSL version will be available at <http://compat.mozilla.org> and will
redirect to the HTTPS version.  This site is for documentation, example code,
and example presentations.

The documentation site is not editable from the browser.  It uses
gettext-style translations.  en-US will be the first supported language.

The two sites are served from a single codebase, at
<https://github.com/mozilla/compat-api>.  Technologies include:

* [Django 1.6](https://docs.djangoproject.com/en/1.6/), a web framework
* [Django REST Framework](http://www.django-rest-framework.org), an API
  framework


# Resources

Resources are simple objects supporting CRUD operations.  Read operations
can be done anonymously.  Creating and updating require account permissions,
and deleting requires admin account permissions.

## Browsers

A **browser** is a brand of web client that has one or more versions.  This
follows most user's understanding of browsers, i.e., `firefox` represents
desktop Firefox, `safari` represents desktop Safari, and `firefox-mobile`
represents Firefox Mobile.

To get the list of browsers:


    GET /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browsers": [{
            "id": "1",
            "slug": "chrome",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/chrome.png",
            "name": {
                "en-US": "Chrome",
            },
            "engine": null,
            "links": {
                "versions": ["123"]
            }
        },{
            "id": "2",
            "slug": "firefox",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en-US": "Firefox",
            },
            "engine": {
                "en-US": "Gecko",
            },
            "links": {
                "versions": ["124"]
            }
        }],
        "links": {
            "versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions",
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


To get an individual browser:


    GET /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browsers": {
            "id": "2",
            "slug": "firefox",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": {
                "en-US": "Firefox (Gecko)",
            },
            "engine": {
                "en-US": "Gecko",
            }
        },
        "links": {
            "versions": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browsers.versions}",
                "type": "browser-versions"
            }
        }
    }


## Browser Versions

A **browser-version** is a specific release of a Browser.

To get the list of browser-versions:


    GET /browser-versions HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browser-versions": [{
            "id": "123",
            "version": "1.0",
            "engine_version": null,
            "current": false,
            "links": {
                "browser": "1",
                "previous": null,
                "next": "176",
                "feature-supports": ["1125", "1126", "1127", "1128", "1129"]
            }
        },{
            "id": "124",
            "version": "18.0",
            "engine_version": "18.0",
            "current": false,
            "links": {
                "browser": "2",
                "previous": "122",
                "next": "176",
                "feature-supports": ["1212", "1213", "1214", "1215", "1216"]
            }
        },{
            "id": "129",
            "version": "30.0",
            "engine_version": "30.0",
            "current": true,
            "links": {
                "browser": "2",
                "previous": "128",
                "next": null,
                "feature-supports": ["1536", "1537", "1538", "1539", "1540"]
            }
        }],
        "links": {
            "browser-versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.browser}",
                "type": "browsers"
            },
            "browser-versions.previous": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.previous}",
                "type": "browser-versions"
            },
            "browser-versions.previous": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.next}",
                "type": "browser-versions"
            },
            "browser-versions.feature-supports": {
                "href": "https://api.compat.mozilla.org/browser-version-features/{browser-versions.features}",
                "type": "browser-version-features"
            }
        },
        "meta": {
            "pagination": {
                "browser-versions": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/browser-versions?page=2&per_page=10",
                    "pages": 14,
                    "per_page": 10,
                    "total": 134,
                }
            }
        }
    }


To get a single browser version:


    GET /browser-versions/123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browser-versions": {
            "id": "123",
            "version": "1.0",
            "engine_version": null,
            "current": false,
            "links": {
                "browser": "1",
                "previous": null,
                "next": "176",
                "feature-supports": ["1125", "1126", "1127", "1128", "1129"]
            }
        },
        "links": {
            "browser-versions.browser": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.browser}",
                "type": "browsers"
            },
            "browser-versions.previous": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.previous}",
                "type": "browser-versions"
            },
            "browser-versions.previous": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.next}",
                "type": "browser-versions"
            },
            "browser-versions.feature-supports": {
                "href": "https://api.compat.mozilla.org/browser-version-features/{browser-versions.features}",
                "type": "browser-version-features"
            }
        }
    }


# Features

A **Feature** is a precise web technology, such as the value `cover` for the CSS
`background-size` property.

To get the list of features:

    GET /features HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "features": [{
            "id": "276",
            "slug": "css-background-size-contain",
            "experimental": false,
            "name": {
                "en-US": "background-size: contain",
            },
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-supports": ["1125", "1212", "1536"]
            }
        },{
            "id": "277",
            "slug": "css-background-size-cover",
            "experimental": false,
            "name": {
                "en-US": "background-size: cover",
            },
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-supports": ["1126", "1213", "1537"]
            }
        },{
            "id": "289",
            "slug": "css-display-grid",
            "experimental": true,
            "name": {
                "en-US": "display: grid",
            },
            "links": {
                "feature-set": "398",
                "spec-sections": ["489"],
                "browser-version-supports": ["1127", "1214", "1538"]
            }
        }],
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "spec-sections": {
                "href": "https://api.compat.mozilla.org/spec-sections/{features.spec-sections}",
                "type": "spec-sections"
            },
            "browser-version-supports": {
                "href": "https://api.compat.mozilla.org/browser-version-features/{features.browser-version-supports}",
                "type": "browser-version-features"
            }
        },
        "meta": {
            "pagination": {
                "features": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/features?page=2&per_page=10",
                    "pages": 76,
                    "per_page": 10,
                    "total": 754,
                }
            }
        }
    }


To get a specific feature:

    GET /features/276 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "features": {
            "id": "276",
            "slug": "css-background-size-contain",
            "experimental": true,
            "name": {
                "en-US": "background-size: contain",
            },
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-supports": ["1125", "1212", "1536"]
            }
        },
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "spec-sections": {
                "href": "https://api.compat.mozilla.org/spec-sections/{features.spec-sections}",
                "type": "spec-sections"
            }
        }
    }


# Feature Sets

A **Feature Set** organizes features into a heierarchy of logical groups.

To get the list of feature sets:


    GET /features-sets HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "feature-sets": [{
            "id": "301",
            "slug": "css",
            "name": {
                "en-US": "CSS",
            },
            "links": {
                "features": [],
                "parent": null,
                "ancestors": ["301"],
                "siblings": ["300", "301", "302", "303"],
                "children": ["313", "314", "315"],
                "decendants": ["301", "313", "314", "315"],
            }
        },{
            "id": "373",
            "slug": "css-background-size",
            "name": {
                "en-US": "background-size",
            },
            "links": {
                "features": ["275", "276", "277"],
                "parent": "301",
                "ancestors": ["301"],
                "siblings": ["372", "373", "374", "375"],
                "children": [],
                "decendants": ["373"],
            }
        }],
        "links": {
            "feature-sets.features": {
                "href": "https://api.compat.mozilla.org/features/{feature-sets.features}",
                "type": "features"
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
            }
        },
        "meta": {
            "pagination": {
                "feature-sets": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/feature-sets?page=2&per_page=10",
                    "pages": 14,
                    "per_page": 10,
                    "total": 131,
                }
            }
        }
    }


To get a single feature set:


    GET /features-sets/373 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "feature-sets": [{
            "id": "373",
            "slug": "css-background-size",
            "name": {
                "en-US": "background-size",
            },
            "links": {
                "features": ["275", "276", "277"]
                "parent": "301",
                "ancestors": ["301", "373"],
                "siblings": ["372", "373", "374", "375"],
                "children": [],
                "decendants": [],
            }
        }],
        "links": {
            "feature-sets.features": {
                "href": "https://api.compat.mozilla.org/features/{feature-sets.features}",
                "type": "features"
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
            }
        }
    }


The tree structure is represented by the links:

* parent - The parent of this feature set, or null if top-level
* ancestors - The path to the top of the tree, in bread-crumb order, including
  self
* siblings - The feature sets with the same parent, including this one, in
  display order
* children - The feature sets that have this feature set as parent, in display
  order
* decendants - The feature sets under this feature set. including this one,
  in tree order


## Browser Version Features

A **Browser Version Feature** is an assertion of the feature support for a
particular version of a browser.

    GET /browser-version-features HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browser-version-features": [{
            "id": "1123",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "browser-version": "123",
                "feature": "276",
            }
        },{
            "id": "1124",
            "support": "yes",
            "prefix": null,
            "note": null,
            "footnote": null,
            "links": {
                "browser-version": "124",
                "feature": "276",
            }
        },{
            "id": "1256",
            "support": "prefixed",
            "prefix": "-webkit",
            "note": null,
            "footnote": null,
            "links": {
                "browser-version": "123",
                "feature": "295",
            }
        },{
            "id": "1256",
            "support": "yes",
            "prefix": null,
            "note": "(behind a pref)",
            "footnote": "To activate flexbox support, for Firefox 18 amd 19, the user has to change the about:config...",
            "links": {
                "browser-version": "123",
                "feature": "295",
            }
        }],
        "links": {
            "browser-version-features.browser-version": {
                "href": "https://api.compat.mozilla.org/browser-versions/{browser-version-features.browser-version}",
                "type": "browser-versions"
            },
            "browser-version-features.feature": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-version-features.feature}",
                "type": "features"
            }
        },
        "meta": {
            "pagination": {
                "browser-version-features": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/browser-version-features?page=2&per_page=10",
                    "pages": 1057,
                    "per_page": 10,
                    "total": 10564,
                }
            }
        }
    }


To retrieve support for a single feature:


    GET /browser-version-features/1123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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
            }
        }
    }


# Views

A **View** is a read-only combination of resources designed for displaying
data to anonymous users.


# Services

A **Service** provides server functionality that is not tied to the data store.

# Additions to Browser Compatibility Data Architecture

This spec includes changes to the
[Browser Compatibility Data Architecture](https://docs.google.com/document/d/1YF7GJ6kgV5_hx6SJjyrgunqznQU1mKxp5FaLAEzMDl4/edit#)
developed around March 2014.  These changes are:

* browsers
    - slug - human-friendly unique identifier
    - name - converted to localized text
    - environment - either "desktop" or "mobile".  Supports current division of
      browser types on MDN.
    - engine - either the localized engine name or null.  Supports current
      engine version callouts on MDN tables.
* browser-versions
    - current - true if version is recommended for download.  For some
      browsers (IE), may have multiple current versions.
    - previous - ID of previous browser version, or null if first
    - next - ID of next browser version, or null if last
* features
    - slug - human-friendly unique identifier
    - experimental - true if property is experimental.  Supports beaker icon
      on MDN, such as
      [run-in value of display property](https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility)
    - name - converted to localized text
    - spec-sections - replaces spec link
* feature-sets
    - slug - human-friendly unique identifier
    - name - converted to localized text
    - ancestors, siblings, children, decendants - tree relations
* browser-version-features
    - prefix - string prefix to enable, or null if no prefix
    - note - short note, length limited, translated, or null.  Supports inline
      notes currently in use on MDN
    - footnote - longer note, may include code samples, translated, or null.
      Supports extended footnote in use on MDN.

# To Do

* Add attribute and link reference to docs
* Convert text to attribute with links and caching
* Convert specs to attribute with links and caching
* Translated text - linked objects or complex objects?  Look at packages suggested by bug
* Power Queries - for example, feature by slug
