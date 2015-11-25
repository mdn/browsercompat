=============================
browsercompat
=============================

.. image:: https://img.shields.io/travis/mdn/browsercompat/master.svg
    :target: https://travis-ci.org/mdn/browsercompat
    :alt: Build Status

.. image:: https://img.shields.io/coveralls/mdn/browsercompat/master.svg
    :target: https://coveralls.io/r/mdn/browsercompat?branch=master
    :alt: Test Coverage

.. image:: https://img.shields.io/requires/github/mdn/browsercompat.svg
     :target: https://requires.io/github/mdn/browsercompat/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy?template=https://github.com/mdn/browsercompat
    :alt: Deploy

.. Omit badges from docs

The Browser Compatibility API will support compatibility data on the
`Mozilla Developer Network`_.  This currently takes the form of browser
compatibility tables, such as the one on the `CSS display property`_.
The API will help centralize this data, and allow it to be kept consistant
across languages and different presentations.

.. _Mozilla Developer Network: https://developer.mozilla.org
.. _CSS display property: https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility

The project started in December 2013.  The goals, requirements, and current
status are documented on the MozillaWiki_.

.. _MozillaWiki: https://wiki.mozilla.org/index.php?title=MDN/Projects/Development/CompatibilityTables

This project will implement the data store and API for compatibility data
and related resources.

Status
------

The initial v1 API has been implemented.  It uses release candidate 2 (RC2)
of the JSON API specification, which was the current version at the time
(Summer 2014).  This API is compatibile with `Ember.js`_ tools that were current
at the time (1.7.0 with Ember Data 1.0.0 beta 9). The v1 API is being used
to store data scraped from MDN. This process has suggested design
improvements, and the API is being incrementally adjusted.
See the `v1 API docs`_ for details.

`JSON API v1.0`_ was released May 2015, and is quite different from RC2.
Ember 2.0 was released August 2015, integrating Ember Data and supporting the
new JSON API specification.  JSON API v1.0 will be supported in the v2 API,
and both v1 and v2 will be supported until tools have been migrated to the
v2 API.

.. _`Ember.js`: http://emberjs.com
.. _`v1 API docs`: v1/intro.html
.. _`JSON API v1.0`: https://jsonapi.org/format/1.0/

Development
-----------

:Code:           https://github.com/mdn/browsercompat
:Dev Server:     https://browsercompat.herokuapp.com (based on `mdn/browsercompat-data`_)
:Issues:         https://bugzilla.mozilla.org/buglist.cgi?quicksearch=compat-data (tracking bug)

                 https://bugzilla.mozilla.org/showdependencytree.cgi?id=996570&hide_resolved=1 (blocking issues for v1)
:Dev Docs:       https://browsercompat.readthedocs.org

                 https://github.com/mdn/browsercompat/wiki
:Mailing list:   https://lists.mozilla.org/listinfo/dev-mdn
:IRC:            irc://irc.mozilla.org/mdndev

.. _`mdn/browsercompat-data`: https://github.com/mdn/browsercompat-data
