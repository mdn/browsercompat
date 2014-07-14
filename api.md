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

```http
GET /browsers HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

### Retrieve by ID

To get a single **browser**:


```http
GET /browsers/2 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

### Retrieve by Slug

To get a **browser** by slug:

```http
GET /browsers/firefox HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

### Create

Creating **browser** instances require authentication with create privileges.
To create a new **browser** instance, POST a representation with at least the
required parameters.  Some items (such as the `id` attribute and the
`history-current` link) will be picked by the server, and will be ignored if
included.

Here's an example of creating a **browser** instance:

```http
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
```

```http
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
```

This, and other methods that change resources, will create a new
**changeset**, and associate the new **browsers-history** with that
**changeset**.  To assign to an existing changeset, add it to the URI:

```http
POST /browsers?changeset=176 HTTP/1.1
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
```

### Update

Updating a **browser** instance require authentication with create privileges.
Some items (such as the `id` attribute and `history` links) can not be
changed, and will be ignored if included.  A successful update will return a
`200 OK`, add a new ID to the `history` links list, and update the
`history-current` link.

To update a **browser**:

```http
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
```

```http
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
```

### Partial Update

An update can just update some fields:

```http
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
```

```http
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
```

### Reverting to a previous version

To revert to an earlier version, set the `history-current` link to a
previous value.  This resets the content and creates a new
**browsers-history** object.

```http
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
```

```http
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
```

### Deletion

To delete a **browser**:

```http
DELETE /browsers/2 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
Authorization: Bearer mF_9.B5f-4.1JqM
```

```http
HTTP/1.1 204 No Content
```

### Reverting a deletion

To revert a deletion:

```http
PUT /browsers/2 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
Authorization: Bearer mF_9.B5f-4.1JqM
```

```http
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
```

## Browser Versions

A **browser-version** is a specific release of a Browser.

The **browser-versions** representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **version** *(write-once)* - Version of browser, or null
      if unknown (for example, to document support for features in early HTML)
    - **engine-version** *(write-once)* - Version of browser engine, or null
      if not tracked
    - **current** - true if this version is recommended for download, false if
      this has been replaced by a new version
* **links**
    - **previous** *(one or null)* - The previous **browser-version**, or null
      if first version or out-of-sequence
    - **next** *(one or null)* - The next **browser-version**, or null if most
      recent version or out-of-sequence
    - **browser-version-features** *(many)* - Associated **browser-version-features**
    - **history-current** *(one)* - Current **browsers-versions-history**
    - **history** *(many)* - Associated **browser-versions-history**, in time
      order (most recent first)


To get a single **browser-version**:

```http
GET /browser-versions/123 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

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

```http
GET /features/276 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

## Feature Sets

A **feature-set** organizes features into a heierarchy of logical groups.  A
**feature-set** corresponds to a page on [MDN](https://developer.mozilla.org),
which will display a list of specifications and a browser compatibility table.

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

```http
GET /features-sets/373 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

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

```http
GET /browser-version-features/1123 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
```

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

```http
GET /specifications/273 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vn.api+json
```

```http
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
}
```

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

```http
GET /specification-sections/792 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vn.api+json
```

```http
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
```

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

```http
GET /specification-statuses/49 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vn.api+json
```

```http
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
```

# Change Control Resources

Change Control Resources help manage changes to resources.

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
    - **changesets** *(many)* - Associated **changesets**
    - **browsers-history** *(many)* - Associated **browsers-history**
    - **browser-versions-history** *(many)* - Associated
      **browser-versions-history**
    - **features-history** *(many)* - Associated **features-history**
    - **feature-sets-history** *(many)* - Associated **feature-sets-history**
    - **browser-version-features-history** *(many)* - Associated
      **browser-version-features-history**


To get a single **user** representation:

```http
GET /users/42 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
            "changesets": "73"
        }
    },
    "links": {
        "users.changesets": {
            "href": "https://api.compat.mozilla.org/changesets/{users.changesets}",
            "type": "changesets"
        }
    }
}
```

If a client is authenticated, the logged-in user's account can be retrieved with:

```http
GET /users/me HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

## Changesets

A **changeset** collects history resources into a logical unit, allowing for
faster reversions and better history display.  The **changeset** can be
auto-created through a `POST`, `PUT`, or `DELETE` to a resource, or it can
be created independently and specified by adding `changeset=<ID>` URI
parameter (i.e., `PUT /browsers/15?changeset=73`).

The representation includes:

* **attributes**
    - **id** *(server selected)* - Database ID
    - **created** *(server selected)* - UTC timestamp of when this changeset
      was created
    - **modified *(server selected)* - UTC timestamp of when this changeset
      was last modified
    - **target-resource** *(write-once)* - The name of the primary resource
      for this changeset, for example "browsers", "browser-versions", etc.
    - **target-resource-id** *(write-once)* - The ID of the primary resource
      for this changeset.
* **links**
    - **user** *(one)* - The user who initiated this changeset
    - **browsers-history** *(many)* - Associated **browsers-history**
    - **browser-versions-history** *(many)* - Associated
      **browser-versions-history**
    - **features-history** *(many)* - Associated **features-history**
    - **feature-sets-history** *(many)* - Associated **feature-sets-history**
    - **browser-version-features-history** *(many)* - Associated
      **browser-version-features-history**


To get a single **changeset** representation:

```http
GET /changeset/73 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.api+json

{
    "changesets": {
        "id": "73",
        "created": "1405353048.910000",
        "modified": "1405353048.910000",
        "target-resource": "feature-sets",
        "target-resource-id": "35",
        "links": {
            "user": "42",
            "browsers-history": [],
            "browser-versions-history": [],
            "features-history": [],
            "feature-sets-history": [],
            "browser-version-features-history": ["1789", "1790"]
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
```

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
    - **changeset** *(one)* - Associated **changeset**

To get a single **browsers-history** representation:

```http
GET /browsers-history/1002 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
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
            "changeset": "1",
        }
    },
    "links": {
        "browsers-history.browser": {
            "href": "https://api.compat.mozilla.org/browser-history/{browsers-history.browser}",
            "type": "browsers"
        },
        "browsers-history.changeset": {
            "href": "https://api.compat.mozilla.org/changesets/{browsers-history.changeset}",
            "type": "changeset"
        }
    }
}
```

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

A **View** is a combination of resources for a particular presentation.  It is
suitable for anonymous viewing of content.

It is possible that views are unnecessary, and could be constructed by
supporting optional parts of the JSON API spec, such as
[Inclusion of Linked Resources](http://jsonapi.org/format/#fetching-includes).
These views are written as if they are aliases for a fully-fleshed
implementation of JSON API.

## View a Feature Set

This view collects the data for a **feature-set**, including the related
resources needed to display it on MDN.

Here is a simple example, the view for the HTML element
[address](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address):

```http
GET /views/view-by-feature-set/html-address HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
```

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.api+json

{
    "feature-sets": {
        "id": "816"
        "slug": "html-address",
        "name": {
            "en": "address"
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
                "experimental": false,
                "name": {
                    "en": "Basic support"
                },
                "links": {
                    "feature-set": "816",
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
                "current": false,
                "links": {
                    "browser": "1",
                    "previous": null,
                    "next": "null",
                    "browser-version-features": ["158", "258", "358", "458"],
                    "history-current": "1567",
                    "history": ["1567"]
                }
            }, {
                "id": "759",
                "version": "1.0",
                "engine-version": "1.7",
                "current": false,
                "links": {
                    "browser": "2",
                    "previous": null,
                    "next": "1253",
                    "browser-version-features": ["159", "259", "359", "459"],
                    "history-current": "1568",
                    "history": ["1568"]
                }
            }, {
                "id": "760",
                "version": "1.0",
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "3",
                    "previous": null,
                    "next": "923",
                    "browser-version-features": ["160", "260", "360", "460"],
                    "history-current": "1569",
                    "history": ["1569"]
                }
            }, {
                "id": "761",
                "version": "5.12",
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "4",
                    "previous": "234",
                    "next": "924",
                    "browser-version-features": ["161", "261", "361", "461"],
                    "history-current": "1570",
                    "history": ["1570"]
                }
            }, {
                "id": "762",
                "version": "1.0",
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "5",
                    "previous": null,
                    "next": "1224",
                    "browser-version-features": ["162", "262", "362", "462"],
                    "history-current": "1571",
                    "history": ["1571"]
                }
            }, {
                "id": "763",
                "version": null,
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "6",
                    "previous": null,
                    "next": null,
                    "browser-version-features": ["163", "263", "363", "463"],
                    "history-current": "1572",
                    "history": ["1572"]
                }
            }, {
                "id": "764",
                "version": "1.0",
                "engine-version": "1.7",
                "current": false,
                "links": {
                    "browser": "7",
                    "previous": null,
                    "next": null,
                    "browser-version-features": ["164", "264", "364", "464"],
                    "history-current": "1574",
                    "history": ["1574"]
                }
            }, {
                "id": "765",
                "version": null,
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "8",
                    "previous": null,
                    "next": null,
                    "browser-version-features": ["165", "265", "365", "465"],
                    "history-current": "1575",
                    "history": ["1575"]
                }
            }, {
                "id": "766",
                "version": null,
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "11",
                    "previous": null,
                    "next": null,
                    "browser-version-features": ["166", "266", "366", "466"],
                    "history-current": "1576",
                    "history": ["1576"]
                }
            }, {
                "id": "767",
                "version": null,
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "9",
                    "previous": null,
                    "next": null,
                    "browser-version-features": ["167", "267", "367", "467"],
                    "history-current": "1577",
                    "history": ["1577"]
                }
            }, {
                "id": "768",
                "version": null,
                "engine-version": null,
                "current": false,
                "links": {
                    "browser": "10",
                    "previous": null,
                    "next": null,
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
```

The process for using this representation is:

1. Parse into an in-memory object store,
2. Create the "Specifications" section:
    1. Add the `Specifications` header
    2. Create an HTML table with a header row "Specification", "Status", "Comment"
    3. For each id in feature-sets.links.specification-sections (`["746", "421", "70"]`):
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
        * Add the first column: the translated feature name
        * For each browser id in meta.compat-table-important:
            - Get the important browser-version-feature IDs from
              meta.compat-table-important.browser-version-features.<`feature ID`>.<`browser ID`>
            - If null, then display "?"
            - If just one, display "<`version`> (<`engine version`>)",
              "<`version`>", or "<`support`>", depending on the defined attributes
            - If multiple, display as subcells
            - Add prefixes, notes, and footnotes links as appropriate
    5. Close each table, add an edit button
    6. Add footnotes for displayed browser-version-features

This may be done by including the JSON in the page as sent over the wire,
or loaded asynchronously, with the tables built after initial page load.

This can also be used by a
["caniuse" table layout](https://wiki.mozilla.org/MDN/Development/CompatibilityTables/Data_Requirements#1._CanIUse_table_layout)
by ignoring the meta section and displaying all the included data.  This will
require more client-side processing to generate, or additional data in the
`<meta>` section.

### Updating Views with Changesets

Updating the page requires a sequence of requests.  For example, if a user
wants to change Chrome support for `<address>` from an unknown version to
version 1, you'll have to create the **browser-version** for that version,
then add the **browser-version-feature** for the support.

The first step is to create a **changeset** as an authenticated user:

```http
POST /changesets/ HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
Authorization: Bearer mF_9.B5f-4.1JqM
Content-Type: application/vnd.api+json

{
    "changesets": {
        "target-resource": "feature-sets",
        "target-resource-id": "816"
    }
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/vnd.api+json
Location: https://api.compat.mozilla.org/changesets/5284

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
```

Next, use the **changeset** ID when creating the **browser-version**:

```http
POST /browser-versions/?changeset=5284 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
Authorization: Bearer mF_9.B5f-4.1JqM
Content-Type: application/vnd.api+json

{
    "browser-versions": {
        "version": "1",
        "links": {
            "browser": "1",
        }
    }
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/vnd.api+json
Location: https://api.compat.mozilla.org/browser-versions/4477

{
    "browser-versions": {
        "id": "4477",
        "version": "1",
        "engine-version": null,
        "current": false,
        "links": {
            "browser": "1",
            "previous": null,
            "next": "null",
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
```

Finally, create the **browser-version-feature**:

```http
POST /browser-version-features/?changeset=5284 HTTP/1.1
Host: api.compat.mozilla.org
Accept: application/vnd.api+json
Authorization: Bearer mF_9.B5f-4.1JqM
Content-Type: application/vnd.api+json

{
    "browser-version-features": {
        "support": "yes",
        "links": {
            "browser-version": "4477",
            "feature": "191"
        }
    }
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/vnd.api+json
Location: https://api.compat.mozilla.org/browser-version-features/8219

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
```
The **browser-versions-history** and **browser-version-features-history**
resources will both refer to **changeset** 5284, and this **changeset** is
linked to **feature-set** 816, despite the fact that no changes were made
to the **feature-set**.  This will facilitate displaying a history of
the compatibility tables, for the purpose of reviewing changes and reverting
vandalism.

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
    - **experimental** - true if feature is experimental.  Supports beaker
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
* If we succeed, we'll have a detailed history of browser support for each
  feature.  For example, the datastore will know that every version of Firefox
  supported the `<h1>` tag.  How should version history be summarized for the
  Browser Compatibility table?  Should the API pick the "important" versions,
  and the KumaScript display them all?  Or should the API send all known
  versions, and the KumaScript parse them for the significant versions, with
  UX for exposing known versions?  The view doc proposes one implementation,
  with a `<meta>` section for identifying the important bits.
* Do we want to add more items to browser-versions?  Here's the Wikipedia
  release history for
  [Chrome](http://en.wikipedia.org/wiki/Google_Chrome_complete_version_history#Release_history)
  and
  [Firefox](http://en.wikipedia.org/wiki/Firefox_release_history#Release_history).
  Some possibly useful additions: release date, retirement date, codename,
  JS engine version, operating system, notes.  It feels like we should import
  the data from version-specific KumaScripts like
  [CompatGeckoDesktop](https://developer.mozilla.org/en-US/docs/Template:CompatGeckoDesktop)
  (versions, release dates, translations, links to release docs).
* We'll need additional models for automated browser testing.  Things like
  user agents, test names, test results for a user / user agent.  And, we'll
  need a bunch of rules for mapping test results to features, required number
  of tests before we'll say a browser supports a feature, what to do with
  test conflicts, etc.  It might be easier to move all those wishlist items to
  a different project, that talks to this API when it's ready to assert
  browser support for a feature.
* I added an 'experimental' attribute to feature.  Do we need additional
  flags?  See "non-standard" in
  [caption-side](https://developer.mozilla.org/en-US/docs/Web/CSS/caption-side#Browser_compatibility),
  "unimplemented" in
  [@font-face](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face#Browser_compatibility),
  "warning" on
  [length](https://developer.mozilla.org/en-US/docs/Web/CSS/length#Browser_compatibility),
  and "fix me" on
  [line-break](https://developer.mozilla.org/en-US/docs/Web/CSS/line-break#Browser_compatibility).

## To Do

* Add multi-get to browser doc, after deciding on
  `GET /browser-versions/1,2,3,4` vs.
  `GET /browser/1/browser-versions`
* Look at additional MDN content for items in common use
* Move to developers.mozilla.org subpath, auth changes

<!--
# vi:syntax=md
-->
