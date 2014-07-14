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

**Contents**
<!--TOC-->

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
* [django-oauth2-provider](https://github.com/caffeinehit/django-oauth2-provider),
  for script-based updates of content

# Resources

Resources are simple objects supporting CRUD operations.  Read operations
can be done anonymously.  Creating and updating require account permissions,
and deleting requires admin account permissions.

All resources support similar operations using HTTP methods:

* `GET /<type>` - List instances (paginated)
* `POST /<type>` - Create new instance
* `GET /<type>/<id>` - Retrieve an instance
* `PUT /<type>/<id>` - Update an instance
* `DELETE /<type>/<id>` - Delete instance

Additional features may be added as needed.  See the
[JSON API docs](http://jsonapi.org/format/) for ideas and what format they
will take.

Because the operations are similar, only **browsers** has complete operations
examples, and others just show retrieving an instance (`GET /<type>/<id>`).

## Browsers

A **browser** is a brand of web client that has one or more versions.  This
follows most users' understanding of browsers, i.e., `firefox` represents
desktop Firefox, `safari` represents desktop Safari, and `firefox-mobile`
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
    - **versions** *(many)* - Associated **browser-versions**
    - **history-current** *(one)* - Current **browsers-history**
    - **history** *(many)* - Associated **browsers-history** in time order
      (most recent first)

### List

To get the paginated list of **browsers**:


    GET /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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
                "versions": ["123"],
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
                "versions": ["124"],
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
                "versions": ["125", "167", "178"],
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
                "versions": ["126"],
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
                "versions": ["127"],
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
                "versions": ["128"],
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
                "versions": ["129"],
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
                "versions": ["130"],
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
                "versions": ["131"],
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
                "versions": ["132"],
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

### Create

Creating **browser** instances require authentication with create privileges.
To create a new **browser** instance, POST a representation with at least the
required parameters.  Some items (such as the `id` attribute and the
`history-current` link) will be picked by the server, and will be ignored if
included.

Here's an example of creating a **browser** instance:

    POST /browsers HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM
    Content-Type: application/vnd.api+json

    {
        "browsers": {
            "slug": "amazon-silk-mobile",
            "environment": "mobile",
            "name": {
                "en": "Amazon Silk Mobile"
            }
        }
    }


The successful response:


    HTTP/1.1 201 Created
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/browsers/15

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

### Retrieve by ID

To get a single **browser**:


    GET /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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

### Retrieve by Slug

To get a **browser** by slug:


    GET /browsers/firefox HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json
    Location: https://api.compat.mozilla.org/browsers/2

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

### Update

Updating a **browser** instance require authentication with create privileges.
Some items (such as the `id` attribute and `history` links) can not be
changed, and will be ignored if included.  A successful update will return a
`200 OK`, add a new ID to the `history` links list, and update the
`history-current` link.

To update a **browser**:

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

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


The successful response is:


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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


### Partial Update

An update can just update some fields:


    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "browsers": {
            "name": {
                "en": "M$ Internet Exploder 💩"
            }
        }
    }


The successful response is:

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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

### Reverting to a previous version

To revert to an earlier version, set the `history-current` link to a
previous value.  This resets the content and creates a new
**browsers-history** object.

    PUT /browsers/3 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "browsers": {
            "links": {
                "history-current": "1003"
            }
        }
    }


A successful response:

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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


### Deletion

To delete a **browser**:


    DELETE /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM


    HTTP/1.1 204 No Content


### Reverting a deletion

To revert a deletion:


    PUT /browsers/2 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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
    - **specification-sections** *(many)* - Associated **specification-sections**
    - **browser-version-features** *(many)* - Associated **browser-version-features**
    - **history-current** *(one)* - Current **features-history**
    - **history** *(many)* - Associated **features-history**, in time order
      (most recent first)

To get a specific **feature**:

    GET /features/276 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "features": {
            "id": "276",
            "slug": "css-background-size-contain",
            "experimental": false,
            "name": {
                "en": "background-size: contain"
            },
            "links": {
                "feature-set": "373",
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


## Feature Sets

A **feature-set** organizes features into a heierarchy of logical groups.

The **feature-sets** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **slug** *(write-once)* - Unique, human-friendly slug
    - **name** *(localized)* - Feature set name
* **links**
    - **features** *(many)* - Associated **features**
    - **specification-sections** *(many)* - Associated
      **specification-sections**
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


To get a single **feature set**:


    GET /features-sets/373 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "feature-sets": {
            "id": "373",
            "slug": "css-background-size",
            "name": {
                "en": "background-size"
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


To get a single **browser-version-features**:


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


## Specifications

A **specification** is a standards document that specifies a web technology.

The **specification** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **kuma-key** - The key for the KumaScript macros
      [SpecName](https://developer.mozilla.org/en-US/docs/Template:SpecName)
      and
      [Spec2](https://developer.mozilla.org/en-US/docs/Template:Spec2),
      used as a data source.
    - **name** *(localized)* - Specification name
    - **uri** *(localized)* - Specification URI, without subpath and anchor
* **links**
    - **specification-sections** *(many)* - Associated **specification-sections**.
    - **specification-status** *(one)* - Associated **specification-status**

To get a single **specification**:

    GET /specifications/273 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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


## Specification Sections

A **specification-section** refers to a specific area of a **specification**
document.

The **specification-section** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **name** *(localized)* - Section name
    - **subpath** *(localized)* - A subpage (possibly with an #anchor) to get
      to the subsection in the doc.  Can be empty string.
    - **note** *(localized)* - Notes for this section
* **links**
    - **specification** *(one)* - The **specification**
    - **features** *(many)* - The associated **features**
    - **feature-sets** *(many)* - The associated **feature-sets**

To get a single **specification-section**:

    GET /specification-sections/792 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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

## Specification Statuses

A **specification-status** refers to the status of a **specification**
document.

The **specification-status** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **kuma-key** - The value for this status in the KumaScript macro
      [Spec2](https://developer.mozilla.org/en-US/docs/Template:Spec2)
    - **name** *(localized)* - Status name
* **links**
    - **specifications** *(many)* - Associated **specifications**

To get a single **specification-section**:

    GET /specification-statuses/49 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vn.api+json


    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

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


# History Resources

History Resources are created when a Resource is created, updated, or deleted.
By navigating the history chain, a caller can see the changes of a resource
over time.

All history representations are similar, so one example should be enough to
determine the pattern.

## Browsers History

A **browsers-history** represents the state of a **browser** at a point in
time, and who is responsible for that state.  The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **timestamp** *(server selected)* - Timestamp of this change
    - **event** *(server selected)* - The type of event, one of "created",
      "changed", or "deleted"
    - **browsers** - The **browsers** representation at this point in time
* **links**
    - **browser** *(one)* - Associated **browser**
    - **user** *(many)* - The user responsible for this change

To get a single **browsers-history** representation:


    GET /browsers-history/1002 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "browsers-history": {
            "id": "1002",
            "timestamp": "1404919464.559140",
            "event": "created",
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

## Users

A **user** represents a person or process that creates, changes, or deletes a
resource.

The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **username** - The user's email or ID
    - **created** *(server selected)* - UTC timestamp of when this user
      account was created
    - **agreement-version** - The version of the contribution agreement the
      user has accepted.  "0" for not agreed, "1" for first version, etc.
    - **permissions** - A list of permissions.  Permissions include:
        * "change-browser-version-feature" - Add or change a
          **browser-version-feauture**
        * "change-resource" - Add or change any resource except **users** or
          history resources
        * "change-user" - Change a **user** resource
        * "delete-resource" - Delete any resource
* **links**
    - **browsers-history** *(many)* - Associated **browsers-history**
    - **browser-versions-history** *(many)* - Associated
      **browser-versions-history**
    - **features-history** *(many)* - Associated **features-history**
    - **feature-sets-history** *(many)* - Associated **feature-sets-history**
    - **browser-version-features-history** *(many)* - Associated
      **browser-version-features-history**


To get a single **user** representation:

    GET /users/42 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "users": {
            "id": "42",
            "username": "askDNA@tdv.com",
            "created": "1405000551.750000",
            "agreement-version": "1",
            "permissions": ["change-browser-version-feature"],
            "links": {
                "browsers-history": [],
                "browser-versions-history": [],
                "features-history": [],
                "feature-sets-history": [],
                "browser-version-features-history": ["1789", "1790"]
            }
        },
        "links": {
            "users.browsers-history": {
                "href": "https://api.compat.mozilla.org/browsers-history/{users.browsers-history}",
                "type": "browsers-history"
            },
            "users.browser-versions-history": {
                "href": "https://api.compat.mozilla.org/browser-versions-history/{users.browser-versions-history}",
                "type": "browser-versions-history"
            },
            "users.features-history": {
                "href": "https://api.compat.mozilla.org/features-history/{users.features-history}",
                "type": "features-history"
            },
            "users.feature-sets-history": {
                "href": "https://api.compat.mozilla.org/feature-sets-history/{users.feature-sets-history}",
                "type": "feature-sets-history"
            },
            "users.browser-version-features-history": {
                "href": "https://api.compat.mozilla.org/browser-version-features-history/{users.browser-version-features-history}",
                "type": "browser-version-features-history"
            }
        }
    }

If a client is authenticated, the logged-in user's account can be retrieved with:


    GET /users/me HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json


# Views

A **View** is a combination of resources for a particular presentation.  It is
suitable for anonymous viewing of content and for updating by a user with the
appropriate permissions.

It is possible that views are unnecessary, and could be constructed by
supporting optional parts of the JSON API spec, such as
[Inclusion of Linked Resources](http://jsonapi.org/format/#fetching-includes).
These views are written as if they are aliases for a fully-fleshed
implementation.

## Specifications by Feature

This view collects the specifications for a feature.  It is used for the
Specifications section of a simple technology.

Here is the call for the HTML element
[address](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address):


    GET /views/specifications-by-feature/html-address HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "features": {
            "id": "191",
            "slug": "html-address",
            "experimental": false,
            "name": {
                "en": "<address>"
            },
            "links": {
                "feature-set": "816",
                "specification-sections": ["746", "421", "70"],
                "browser-version-features": ["358", "543", "975"],
                "history-current": "395",
                "history": ["395"]
            }
        },
        "linked": {
            "specification-sections": [{
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
                    "features": ["275", "276", "277"]
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
                    "features": ["275", "276", "277"]
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
                    "features": ["275", "276", "277"]
                }
            }],
            "specifications": [{
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
            ],
            "specification-statuses": [{
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
            }]
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

The KumaScript would parse this into an in-memory object store, and then use
it to:

1. Create an HTML table with a header row "Specification", "Status", "Comment"
2. For each id in features.links.specification-sections (`["746", "421", "70"]`):
    * Add the first column: a link to specifications.uri.(lang or en) +
      specifications-sections.subpath.(lang or en), with link text
      specifications.name.(lang or en), with title based on
      specification-sections.name.(lang or en) or feature.name.(lang or en).
    * Add the second column: A span with class
      "spec-" + specification-statuses.kuma-key, and the text
      specification-statuses.name.(lang or en).
    * Add the third column:
      specification-statuses.notes.(land or en), or empty string
3. Close the table, and add an edit button.

Editing a specification may require additional requests, such as
authenticating the user to the API and fetching the list of specifications
to populate a dropdown.

Updating the specification table requires a PUT to the API, with the complete
or partial representation.  For example, to add a note to the HTML 4.01 spec:


    PUT /views/specifications-by-feature/html-address HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "linked": {
            "specification-sections": {
                "id": "70",
                "notes": {
                    "en": "Don't write as ADDRESS; uppercase isn't cool anymore."
                }
            }
        }
    }


The response will be the full representation with the accepted changes, or an
error.

Alternatively, the change can be sent to the resource itself:

    PUT /specification-sections/70 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "specification-sections": {
            "notes": {
                "en": "Don't write as ADDRESS; uppercase isn't cool anymore."
            }
        }
    }


Other edits, such as deleting or creating resources, may need to be done as
independant API calls.

## Specifications by Feature Set

This view collects the specifications for a feature set.  It is used for the
Specifications section of a complex technology.

Here is the call for the CSS property
[display](https://developer.mozilla.org/en-US/docs/Web/CSS/display):


    GET /views/specifications-by-feature-set/css-display HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json

    HTTP/1.1 200 OK
    Content-Type: application/vnd.api+json

    {
        "feature-sets": {
            "id": "780",
            "slug": "css-display",
            "name": {
                "en": "display"
            },
            "links": {
                "features": ["7633", "7634", "7635", "7636", "7637", "7638", "7639", "7640", "7641", "7642"],
                "specification-sections": ["9481", "9482", "9483", "9484", "9485"],
                "parent": "301",
                "ancestors": ["301", "780"],
                "siblings": ["778", "779", "780", "781", "782"],
                "children": [],
                "decendants": [],
                "history-current": "648",
                "history": ["648"]
            }
        },
        "linked": {
            "features": [{
                "id": "7633",
                "slug": "css-display-basic",
                "experimental": false,
                "name": {
                    "en": "<code>none<\/code>, <code>inline<\/code>, and <code>block<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3138", "3139", "3140", "3141", "3142"],
                    "history-current": "456",
                    "history": ["456"]
                }
            }, {
                "id": "7634",
                "slug": "css-display-inline-block",
                "experimental": false,
                "name": {
                    "en": "<code>inline block<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3238", "3239", "3240", "3241", "3242"],
                    "history-current": "466",
                    "history": ["466"]
                }
            }, {
                "id": "7635",
                "slug": "css-display-list-item",
                "experimental": false,
                "name": {
                    "en": "<code>list-item<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3338", "3339", "3340", "3341", "3342"],
                    "history-current": "476",
                    "history": ["476"]
                }
            }, {
                "id": "7636",
                "slug": "css-display-run-in",
                "experimental": true,
                "name": {
                    "en": "<code>run-in<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3438", "3439", "3440", "3441", "3442"],
                    "history-current": "486",
                    "history": ["486"]
                }
            }, {
                "id": "7637",
                "slug": "css-display-inline-table",
                "experimental": false,
                "name": {
                    "en": "<code>inline-table<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3538", "3539", "3540", "3541", "3542"],
                    "history-current": "496",
                    "history": ["496"]
                }
            }, {
                "id": "7638",
                "slug": "css-display-table",
                "experimental": false,
                "name": {
                    "en": "<code>table<\/code>, <code>table-cell<\/code>, <code>table-column<\/code>, <code>table-colgroup<\/code>, <code>table-header-group<\/code>, <code>table-row-group<\/code>, <code>table-footer-group<\/code>, <code>table-row<\/code>, and <code>table-caption<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3638", "3639", "3640", "3641", "3642"],
                    "history-current": "506",
                    "history": ["506"]
                }
            }, {
                "id": "7639",
                "slug": "css-display-flex",
                "experimental": false,
                "name": {
                    "en": "<code>flex<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3738", "3739", "3740", "3741", "3742"],
                    "history-current": "516",
                    "history": ["516"]
                }
            }, {
                "id": "7640",
                "slug": "css-display-inline-flex",
                "experimental": false,
                "name": {
                    "en": "<code>inline-flex<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3838", "3839", "3840", "3841", "3842"],
                    "history-current": "526",
                    "history": ["526"]
                }
            }, {
                "id": "7641",
                "slug": "css-display-grid",
                "experimental": yes,
                "name": {
                    "en": "<code>grid<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["3938", "3939", "3940", "3941", "3942"],
                    "history-current": "536",
                    "history": ["536"]
                }
            }, {
                "id": "7641",
                "slug": "css-display-inline-grid",
                "experimental": yes,
                "name": {
                    "en": "<code>inline-grid<\/code>"
                },
                "links": {
                    "feature-set": "780",
                    "specification-sections": [],
                    "browser-version-features": ["4038", "4039", "4040", "4041", "4042"],
                    "history-current": "546",
                    "history": ["546"]
                }
            }],
            "specification-sections": [{
                "id": "9481",
                "name": {
                    "en": "display"
                },
                "subpath": {
                    "en": "#display"
                },
                "notes": {
                    "en": "Added the <code>run-in<\/code> value."
                },
                "links": {
                    "specification": "81",
                    "features": [],
                    "feature-sets": ["780"]
                }
            }, {
                "id": "9482",
                "name": {
                    "en": "display"
                },
                "subpath": {
                    "en": "#grid-declaration0"
                },
                "notes": {
                    "en": "Added the grid box model values."
                },
                "links": {
                    "specification": "82",
                    "features": [],
                    "feature-sets": ["780"]
                }
            }, {
                "id": "9483",
                "name": {
                    "en": "display"
                },
                "subpath": {
                    "en": "#flex-containers"
                },
                "notes": {
                    "en": "Added the flexible box model values."
                },
                "links": {
                    "specification": "83",
                    "features": [],
                    "feature-sets": ["780"]
                }
            }, {
                "id": "9484",
                "name": {
                    "en": "display"
                },
                "subpath": {
                    "en": "visuren.html#display-prop"
                },
                "notes": {
                    "en": "Added the table mode values and <code>inline-block<\/code>."
                },
                "links": {
                    "specification": "83",
                    "features": [],
                    "feature-sets": ["780"]
                }
            }, {
                "id": "9485",
                "name": {
                    "en": "display"
                },
                "subpath": {
                    "en": "#display"
                },
                "notes": {
                    "en": "Basic values: <code>none,block,inline,<\/code> and <code>list-item<\/code>."
                },
                "links": {
                    "specification": "83",
                    "features": [],
                    "feature-sets": ["780"]
                }
            }],
            "specifications": [{
                "id": "81",
                "kumu-key": "CSS3 Box",
                "name": {
                    "en": "CSS Basic Box Model"
                },
                "uri": {
                    "en": "http://dev.w3.org/csswg/css3-box/"
                },
                "links": {
                    "specification-sections": ["9481"],
                    "specification-status": "24"
                }
            }, {
                "id": "82",
                "kumu-key": "CSS3 Grid",
                "name": {
                    "en": "CSS Grid Layout"
                },
                "uri": {
                    "en": "http://dev.w3.org/csswg/css3-grid-layout/"
                },
                "links": {
                    "specification-sections": ["9482"],
                    "specification-status": "24"
                }
            }, {
                "id": "83",
                "kumu-key": "CSS3 Flexbox",
                "name": {
                    "en": "CSS Flexible Box Layout Module"
                },
                "uri": {
                    "en": "http://dev.w3.org/csswg/css3-flexbox/"
                },
                "links": {
                    "specification-sections": ["9483"],
                    "specification-status": "52"
                }
            }, {
                "id": "84",
                "kumu-key": "CSS2.1"
                "name": {
                    "en": "CSS Level 2 (Revision 1)"
                },
                "uri": {
                    "en": "http://www.w3.org/TR/CSS2/"
                },
                "links": {
                    "specification-sections": ["9484"],
                    "specification-status": "49"
                }
            }, {
                "id": "85",
                "kumu-key": "CSS1"
                "name": {
                    "en": "CSS Level 1"
                },
                "uri": {
                    "en": "http://www.w3.org/TR/CSS1/"
                },
                "links": {
                    "specification-sections": ["9485"],
                    "specification-status": "49"
                }
            }],
            "specification-statuses": [{
                "id": "24",
                "kuma-key": "WD",
                "name": {
                    "en": "Working Draft",
                    "ja": "草案"
                },
                "links": {
                    "specifications": ["81", "82"]
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
            }]
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

The KumaScript would parse this into an in-memory object store, and then use
it to:

1. Create an HTML table with a header row "Specification", "Status", "Comment"
2. For each id in feature-sets.links.specification-sections (`["9481", "9482", ...]`):
    * Add the first column: a link to specifications.uri.(lang or en) +
      specifications-sections.subpath.(lang or en), with link text
      specifications.name.(lang or en), with title based on
      specification-sections.name.(lang or en) or feature.name.(lang or en).
    * Add the second column: A span with class
      "spec-" + specification-statuses.kuma-key, and the text
      specification-statuses.name.(lang or en).
    * Add the third column:
      specification-statuses.notes.(land or en), or empty string
3. Close the table, and add an edit button.

Editing a specification may require additional requests, such as
authenticating the user to the API and fetching the list of specifications
to populate a dropdown.

Updating the specification table requires a PUT to the API, with the complete
or partial representation.  For example, to add a note to the CSS3 Flexbox
spec:


    PUT /views/specifications-by-feature-set/html-address HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "linked": {
            "specification-sections": {
                "id": "83",
                "notes": {
                    "en": "Added the <code>flex, inline-flex<\/code> values."
                }
            }
        }
    }


The response will be the full representation with the accepted changes, or an
error.

Alternatively, the change can be sent to the resource itself:

    PUT /specification-sections/83 HTTP/1.1
    Host: api.compat.mozilla.org
    Accept: application/vnd.api+json
    Authorization: Bearer mF_9.B5f-4.1JqM

    {
        "specification-sections": {
            "notes": {
                "en": "Added the <code>flex, inline-flex<\/code> values."
            }
        }
    }


Other edits, such as deleting or creating resources, may need to be done as
independant API calls.

# Services

A **Service** provides server functionality beyond basic manipulation of
resources.

## Authentication

Several endpoint handle user authentication.

<https://api.compat.mozilla.org/auth> is an HTML page that shows the user's
current authentication status, and includes a button for starting a
[Persona](http://www.mozilla.org/en-US/persona/) login.

One endpoint implements Persona logins.  See the
[Persona Quick Setup](https://developer.mozilla.org/en-US/Persona/Quick_Setup)
for details.

* `/auth/persona/login` - Exchanges a Persona assertion for a login cookie.
  If the email is not on the system, then a new **user** resource is created.
  If the user has not accepted the latest version of the contribution
  agreement, then they are redirected to a page to accept it.  Otherwise, they
  are redirected to /auth.

Four endpoints are used for [OAuth2](http://tools.ietf.org/html/rfc6749),
used to exchange Persona credentials for credentials usable from a server:

* `/auth/oauth2/authorize`
* `/auth/oauth2/authorize/confirm`
* `/auth/oauth2/redirect`
* `/auth/oauth2/access_token`

A final endpoint is used to delete the credential and log out the user:

* `/auth/logout`

## Browser Identification

The `/browser-ident` endpoint provides browser identification based on the
User Agent and other parameters.

Two potential sources for this information:

* [WhichBrowser](https://github.com/NielsLeenheer/WhichBrowser) - Very
  detailed.  Uses User Agent header and feature detection to distinguish
  between similar browsers.  Written in PHP.
* [ua-parser](https://github.com/tobie/ua-parser) - Parses the User Agent.
  The
  [reference parser](https://webplatform.github.io/browser-compat-model/https://webplatform.github.io/browser-compat-model/#reference-user-agent-parser)
  for [WebPlatform.org](http://www.webplatform.org).  Written in Python.

This endpoint will probably require the browser to visit it.  It will be
further speced as part of the UX around user contributions.

# Issues to Resolve Before Code

## Additions to Browser Compatibility Data Architecture

This spec includes changes to the
[Browser Compatibility Data Architecture](https://docs.google.com/document/d/1YF7GJ6kgV5_hx6SJjyrgunqznQU1mKxp5FaLAEzMDl4/edit#)
developed around March 2014.  These seemed like a good idea to me, based on
list threads and thinking how to recreate Browser Compatibility tables live on
MDN.

These changes are:

* **browsers**
    - **slug** - human-friendly unique identifier
    - **name** - converted to localized text.
    - **environment** - either "desktop" or "mobile".  Supports current division
      of browser types on MDN.
    - **engine** - either the localized engine name or null.  Supports current
      engine version callouts on MDN tables.
* **browser-versions**
    - **current** - true if version is recommended for download.  For some
      browsers (IE), may have multiple current versions.
    - **previous** - ID of previous browser version, or null if first
    - **next** - ID of next browser version, or null if last
* **features**
    - **slug** - human-friendly unique identifier
    - **experimental** - true if property is experimental.  Supports beaker
      icon on MDN, such as
      [run-in value of display property](https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility)
    - **name** - converted to localized text
    - **specfication-sections** - replaces spec link
* **feature-sets**
    - **slug - human-friendly unique identifier
    - **name - converted to localized text
    - **ancestors**, **siblings**, **children**, **decendants** - tree relations
* **browser-version-features**
    - **prefix** - string prefix to enable, or null if no prefix
    - **note** - short note, length limited, translated, or null.  Supports
      inline notes currently in use on MDN
    - **footnote** - longer note, may include code samples, translated, or null.
      Supports extended footnote in use on MDN.

There are also additional Resources:

* **users** - For identifying the user who made a change
* **specification-sections** - For referring to a section of a specification, with
  translated titles and anchors
* **specifications** - For referring to a specification, with translated titles
  and URIs.
* All the history resources (**browsers-history**,
  **browser-versions-history**, etc.)

## Unresolved Issues

* We've been talking data models.  This document talks about APIs.
  **The service will not have a working SQL interface**.  Features like
  history require that changes are made through the API.  Make sure your
  use case is supported by the API.
* overholt wants
  [availability in Web Workers](https://bugzilla.mozilla.org/show_bug.cgi?id=996570#c14).
  Is an API enough to support that need?
* I'm not sure if the translatable strings are correct:
    - browsers.name - Firefox explicitly says
      [don't localize our brand](http://www.mozilla.org/en-US/styleguide/communications/translation/#branding).
      I can't find examples of any localized browser names in the wild.
    - browsers.engine - Same
    - features.name - "Basic usage" and "none, inline and block" should be
      localized.  But, are those good feature names?  Could you write a bit of
      JavaScript to test 'Basic usage'?  Should there be three features
      ("display: none", "display: inline", "display: block") instead?  The
      need for translated feature names might be a doc smell.
    - feature-sets.name - Not sure if "CSS", "display", etc. should be
      localized, similar logic to feature names.
* I think Niels Leenheer has good points about browsers being different across
  operating systems and OS versions - I'm considering adding this to the model:
  [Mapping browsers to 2.2.1 Dictionary Browser Members](http://lists.w3.org/Archives/Public/public-webplatform-tests/2013OctDec/0007.html).
* How should we support versioning the API?  There is no Internet concensus.
    - I expect to break the API as needed while implementing.  At some point
      (late 2014), we'll call it v1.
    - Additions, such as new attributes and links, will not cause an API bump
    - Some people put the version in the URL (/v1/browsers, /v2/browsers)
    - Some people use a custom header (`X-Api-Version: 2`)
    - Some people use the Accept header
      (`Accept: application/vnd.api+json;version=2`)
    - These people all hate each other.
      [Read a good blog post on the subject](http://www.troyhunt.com/2014/02/your-api-versioning-is-wrong-which-is.html).
* What should be the default permissions for new users?  What is the process
  for upgrading or downgrading permissions?
* Is Persona a good fit for creating API accounts?  There will need to be a
  process where an MDN user becomes an API user, and a way for an API user
  to authenticate directly with the API.

## To Do

* Convert to fenced code blocks
* Add changesets resource
* feature-sets -> "Page on MDN"
* Change view to read-only, add table data
* Add multi-get to browser doc
* Look at additional MDN content for items in common use
* Move to developers.mozill.org subpath, auth changes

<!--
# vi:syntax=md
-->
