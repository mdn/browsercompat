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
* [django-simple-history](https://django-simple-history.readthedocs.org/en/latest/index.html),
  for recording changes to models
* [django-hvad](http://django-hvad.readthedocs.org/en/latest/public/quickstart.html).
  for translations of human-facing text
* [django-mptt](https://github.com/django-mptt/django-mptt/), for efficiently
  storing hierarchical data

# Resources

Resources are simple objects supporting CRUD operations.  Read operations
can be done anonymously.  Creating and updating require account permissions,
and deleting requires admin account permissions.


## Browsers

A **browser** is a brand of web client that has one or more versions.  This
follows most users' understanding of browsers, i.e., `firefox` represents
desktop Firefox, `safari` represents desktop Safari, and `firefox-mobile`
represents Firefox Mobile.

The **browsers** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **class** - String, must be one of "desktop" or "mobile"
    - **icon** - Protocol-less path to representative icon
    - **name** *(localized)* - Browser name
    - **engine** *(localized)* - Browser engine, or null if not version tracked
* **links**
    - **versions** *(many)* - Associated **browser-versions**
    - **history-current** *(one)* - Current **browsers-history**
    - **history** *(many)* - Associated **browsers-history** in time order
      (most recent first)

To get the list of **browsers**:


    GET /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "browsers": [{
            "id": "1",
            "slug": "chrome",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/chrome.png",
            "name": "Chrome",
            "engine": null,
            "links": {
                "versions": ["123"],
                "history-current": "1001",
                "history": ["1001"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    },
                    "engine": {
                        "selected": null,
                        "available": []
                    }
                }
            }
        },{
            "id": "2",
            "slug": "firefox",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": "Firefox",
            "engine": "Gecko",
            "links": {
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    },
                    "engine": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
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


To get a single **browser**:


    GET /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "browsers": {
            "id": "2",
            "slug": "firefox",
            "class": "desktop",
            "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
            "name": "Firefox",
            "engine": "Gecko",
            "links": {
                "versions": ["124"],
                "history-current": "1002",
                "history": ["1002"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    },
                    "engine": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
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
            }
            "browsers.history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{browsers.history}",
                "type": "browsers-history"
            }
        }
    }

## Browser Versions

A **browser-version** is a specific release of a Browser.

The **browser-versions** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **version** *(write-once)* - Version of browser
    - **engine-version** *(write-once)* - Version of browser engine, or null
      if not tracked
    - **current** - true if this version is recommended for download, false if
      this has been replaced by a new version
* **links**
    - **previous** *(one or null)* - The previous **browser-version**, or null
      if first version
    - **next** *(one or null)* - The next **browser-version**, or null if most
      recent version
    - **browser-version-features** *(many)* - Associated **browser-version-features**
    - **history-current** *(one)* - Current **browsers-versions-history**
    - **history** *(many)* - Associated **browser-versions-history**, in time
      order (most recent first)

To get the list of **browser-versions**:


    GET /browser-versions HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browser-versions": [{
            "id": "123",
            "version": "1.0",
            "engine-version": null,
            "current": false,
            "links": {
                "browser": "1",
                "previous": null,
                "next": "176",
                "browser-version-features": ["1125", "1126", "1127", "1128", "1129"],
                "history-current": "567",
                "history": ["567"]
            }
        },{
            "id": "124",
            "version": "18.0",
            "engine-version": "18.0",
            "current": false,
            "links": {
                "browser": "2",
                "previous": "122",
                "next": "176",
                "browser-version-features": ["1212", "1213", "1214", "1215", "1216"],
                "history-current": "568",
                "history": ["568"]
            }
        },{
            "id": "129",
            "version": "30.0",
            "engine-version": "30.0",
            "current": true,
            "links": {
                "browser": "2",
                "previous": "128",
                "next": null,
                "browser-version-features": ["1536", "1537", "1538", "1539", "1540"],
                "history-current": "569",
                "history": ["569"]
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
            "browser-versions.next": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.next}",
                "type": "browser-versions"
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


To get a single **browser-version**:


    GET /browser-versions/123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browser-versions": {
            "id": "123",
            "version": "1.0",
            "engine-version": null,
            "current": false,
            "links": {
                "browser": "1",
                "previous": null,
                "next": "176",
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
            "browser-versions.previous": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.previous}",
                "type": "browser-versions"
            },
            "browser-versions.next": {
                "href": "https://api.compat.mozilla.org/browsers/{browser-versions.next}",
                "type": "browser-versions"
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

## Features

A **feature** is a precise web technology, such as the value `cover` for the CSS
`background-size` property.

The **features** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **experimental** - true if feature is experimental, should not be used
      in production
    - **name** *(localized)* - Feature name
* **links**
    - **feature-set** *(one)* - Associated **feature-set**
    - **spec-sections** *(many)* - Associated **spec-sections**
    - **browser-version-features** *(many)* - Associated **browser-version-features**
    - **history-current** *(one)* - Current **features-history**
    - **history** *(many)* - Associated **features-history**, in time order
      (most recent first)

To get the list of **features**:

    GET /features HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "features": [{
            "id": "276",
            "slug": "css-background-size-contain",
            "experimental": false,
            "name": "background-size: contain",
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-features": ["1125", "1212", "1536"],
                "history-current": "456",
                "history": ["456"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
            }
        },{
            "id": "277",
            "slug": "css-background-size-cover",
            "experimental": false,
            "name": "background-size: cover",
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-features": ["1126", "1213", "1537"],
                "history-current": "457",
                "history": ["457"]
            }
        },{
            "id": "289",
            "slug": "css-display-grid",
            "experimental": true,
            "name": "display: grid",
            },
            "links": {
                "feature-set": "398",
                "spec-sections": ["489"],
                "browser-version-features": ["1127", "1214", "1538"],
                "history-current": "458",
                "history": ["458"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
            }
        }],
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "features.spec-sections": {
                "href": "https://api.compat.mozilla.org/spec-sections/{features.spec-sections}",
                "type": "spec-sections"
            },
            "features.browser-version-features": {
                "href": "https://api.compat.mozilla.org/browser-version-features/{features.browser-version-features}",
                "type": "browser-version-features"
            },
            "features.history-current": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history-current}",
                "type": "features-history"
            },
            "features.history": {
                "href": "https://api.compat.mozilla.org/features-history/{features.history}",
                "type": "features-history"
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


To get a specific **feature**:

    GET /features/276 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "features": {
            "id": "276",
            "slug": "css-background-size-contain",
            "experimental": false,
            "name": "background-size: contain",
            "links": {
                "feature-set": "373",
                "spec-sections": ["485"],
                "browser-version-features": ["1125", "1212", "1536"],
                "history-current": "456",
                "history": ["456"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
            }
        },
        "links": {
            "features.feature-set": {
                "href": "https://api.compat.mozilla.org/feature-sets/{features.feature-set}",
                "type": "features-sets"
            },
            "features.spec-sections": {
                "href": "https://api.compat.mozilla.org/spec-sections/{features.spec-sections}",
                "type": "spec-sections"
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


## Feature Sets

A **feature-set** organizes features into a heierarchy of logical groups.

The **feature-sets** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **name** *(localized)* - Feature set name
* **links**
    - **features** *(many)* - Associated **features**
    - **parent** *(one or null)* - The **feature-set** one level up, or null
      if top-level
    - **ancestors** *(many)* - The **feature-sets** that form the path to the
      top of the tree, including this one, in bread-crumb order (top to self)
    - **siblings** *(many)* - The **feature-sets** with the same parent,
      including including this one, in display order
    - **children** *(many)* - The **feature-sets** that have this
      **feature-set** as parent, in display order
    - **decendants** *(many)* - The **feature-sets** in the local tree for
      this **feature-set**. including this one, in tree order
    - **history-current** *(one)* - The current **feature-sets-history**
    - **history** *(many)* - Associated **feature-sets-history**, in time
      order (most recent first)


To get the list of feature sets:


    GET /features-sets HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "feature-sets": [{
            "id": "301",
            "slug": "css",
            "name": "CSS",
            "links": {
                "features": [],
                "parent": null,
                "ancestors": ["301"],
                "siblings": ["300", "301", "302", "303"],
                "children": ["313", "314", "315"],
                "decendants": ["301", "313", "314", "315"],
                "history-current": "647",
                "history": ["647"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
            }
        },{
            "id": "373",
            "slug": "css-background-size",
            "name": "background-size",
            "links": {
                "features": ["275", "276", "277"],
                "parent": "301",
                "ancestors": ["301"],
                "siblings": ["372", "373", "374", "375"],
                "children": [],
                "decendants": ["373"],
                "history-current": "648",
                "history": ["648"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
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
            },
            "feature-sets.history-current": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{feature-sets.history-current}",
                "type": "feature-sets-history"
            },
            "feature-sets.history": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{feature-sets.history}",
                "type": "feature-sets-history"
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


To get a single **feature set**:


    GET /features-sets/373 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "feature-sets": [{
            "id": "373",
            "slug": "css-background-size",
            "name": "background-size",
            "links": {
                "features": ["275", "276", "277"],
                "parent": "301",
                "ancestors": ["301", "373"],
                "siblings": ["372", "373", "374", "375"],
                "children": [],
                "decendants": [],
                "history-current": "648",
                "history": ["648"]
            },
            "meta": {
                "translations": {
                    "name": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
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


## Browser Version Features

A **browser-version-feature** is an assertion of the feature support for a
particular version of a browser.

The **browser-version-feature** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **support** - Assertion of support of the **browser-version** for the
      **feature**, one of "yes", "no", "prefixed", "partial", "unknown"
    - **prefix** - Prefix needed, if support is "prefixed"
    - **note** *(localized)* - Short note on support, designed for inline
      display, max 20 characters
    - **footnote** *(localized)* - Long note on support, designed for
      display after a compatibility table, MDN wiki format
* **links**
    - **browser-version** *(one)* - The associated **browser-version**
    - **feature** *(one)* - The associated **feature**
    - **history-current** *(one)* - Current
      **browser-version-features-history**
    - **history** *(many)* - Associated **browser-version-features-history**
      in time order (most recent first)


To get the list of **browser-version-features**:


    GET /browser-version-features HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

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
                "history-current": "2567",
                "history": ["2567"]
            },
            "meta": {
                "translations": {
                    "note": {
                        "selected": null,
                        "available": []
                    },
                    "footnote": {
                        "selected": null,
                        "available": []
                    }
                }
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
                "history-current": "2568",
                "history": ["2568"]
            },
            "meta": {
                "translations": {
                    "note": {
                        "selected": null,
                        "available": []
                    },
                    "footnote": {
                        "selected": null,
                        "available": []
                    }
                }
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
                "history-current": "2569",
                "history": ["2569"]
            },
            "meta": {
                "translations": {
                    "note": {
                        "selected": null,
                        "available": []
                    },
                    "footnote": {
                        "selected": null,
                        "available": []
                    }
                }
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
                "history-current": "2570",
                "history": ["2570"]
            },
            "meta": {
                "translations": {
                    "note": {
                        "selected": "en",
                        "available": ["en"]
                    },
                    "footnote": {
                        "selected": "en",
                        "available": ["en"]
                    }
                }
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
            },
            "browser-version-features.history-current": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{browser-version-features.history-current}",
                "type": "browser-version-features-history"
            },
            "browser-version-features.history": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{browser-version-features.history}",
                "type": "browser-version-features-history"
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


To get a single **browser-version-features**:


    GET /browser-version-features/1123 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

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
            },
            "meta": {
                "translations": {
                    "note": {
                        "selected": null,
                        "available": []
                    },
                    "footnote": {
                        "selected": null,
                        "available": []
                    }
                }
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


# History

History objects are created when a Resource is created, updated, or deleted.
By navigating the history chain, a caller can see the changes of a resource
over time.

All history representations are similar, so one example should be enough to
determine the pattern.

## Browsers History

A **browsers-history** represents the state of a **browser** at a point in
time, and who is responsible for that representation.  The representation
includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **timestamp** *(server selected)* - Timestamp of this change
    - **event** *(server selected)* - The type of event, one of "created",
      "changed", or "deleted"
    - **browsers** - The **browsers** representation at this point in time
* **links**
    - **browser** *(one)* - Associated **browser**
    - **user** *(many)* - The user responsible for this change


To get the list of **browsers-history**:


    GET /browsers-history HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "browsers-history": [{
            "id": "1001",
            "timestamp": "1404919464.559140",
            "event": "created",
            "browsers": {
                "id": "1",
                "slug": "chrome",
                "class": "desktop",
                "icon": "//compat.cdn.mozilla.net/media/img/browsers/chrome.png",
                "name": "Chrome",
                "engine": null,
                "links": {
                    "versions": ["123"],
                    "history-current": "1001",
                    "history": ["1001"]
                },
                "meta": {
                    "translations": {
                        "name": {
                            "selected": "en",
                            "available": ["en"]
                        },
                        "engine": {
                            "selected": null,
                            "available": []
                        }
                    }
                }
            },
            "links": {
                "browser": "1",
                "user": "1",
            }
        }, {
            "id": "1002",
            "timestamp": "1404919464.559140",
            "event": "created",
            "browsers": {
                "id": "2",
                "slug": "firefox",
                "class": "desktop",
                "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
                "name": "Firefox",
                "engine": "Gecko",
                "links": {
                    "versions": ["124"],
                    "history-current": "1002",
                    "history": ["1002"]
                },
                "meta": {
                    "translations": {
                        "name": {
                            "selected": "en",
                            "available": ["en"]
                        },
                        "engine": {
                            "selected": "en",
                            "available": ["en"]
                        }
                    }
                }
            },
            "links": {
                "browser": "1",
                "users": "1",
            }
        }],
        "links": {
            "browsers-history.browser": {
                "href": "https://api.compat.mozilla.org/browser-history/{browsers-history.browser}",
                "type": "browsers"
            },
            "browsers-history.user": {
                "href": "https://api.compat.mozilla.org/users/{browsers-history.user}",
                "type": "users"
            },
        },
        "meta": {
            "pagination": {
                "browsers-history": {
                    "prev": null,
                    "next": "https://api.compat.mozilla.org/browsers-history?page=2&per_page=10",
                    "pages": 2,
                    "per_page": 10,
                    "total": 14,
                }
            }
        }
    }


To get a single **browsers-history** representation:


    GET /browsers-history/1002 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Content-Language: en

    {
        "browsers-history": {
            "id": "1002",
            "timestamp": "1404919464.559140",
            "event": "created",
            "browsers": {
                "id": "2",
                "slug": "firefox",
                "class": "desktop",
                "icon": "//compat.cdn.mozilla.net/media/img/browsers/firefox.png",
                "name": "Firefox",
                "engine": "Gecko",
                "links": {
                    "versions": ["124"],
                    "history-current": "1002",
                    "history": ["1002"]
                },
                "meta": {
                    "translations": {
                        "name": {
                            "selected": "en",
                            "available": ["en"]
                        },
                        "engine": {
                            "selected": "en",
                            "available": ["en"]
                        }
                    }
                }
            },
            "links": {
                "browser": "1",
                "users": "1",
            }
        },
        "links": {
            "browsers-history.browser": {
                "href": "https://api.compat.mozilla.org/browser-history/{browsers-history.browser}",
                "type": "browsers"
            },
            "browsers-history.user": {
                "href": "https://api.compat.mozilla.org/users/{browsers-history.user}",
                "type": "users"
            },
        }
    }

## Browser Versions History

A **browser-versions-history** represents a state of a **browser-version** at
a point in time, and who is responsible for that representation.  See
**browsers-history** and **browser-versions** for an idea of the represention.

## Features History

A **features-history** represents a state of a **feature** at a point in time,
and who is responsible for that representation.  See **browsers-history** and
**features** for an idea of the represention.

## Feature Sets History

A **feature-sets-history** represents a state of a **feature-set** at a point
in time, and who is responsible for that representation.  See
**browsers-history** and **feature-sets** for an idea of the represention.

## Browser Version Features History

A **browser-version-features-history** represents a state of a
**browser-version-feature** at a point in time, and who is responsible for that
representation.  See **browsers-history** and **browser-version-features** for
an idea of the represention.


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

* Add spec models
* Add user models
* Add translations back to main repr
* Power Queries - for example, feature by slug
* Add examples of tables, updating
* Add example of reverting
