=============================
BrowserCompat API
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

The Browser Compatibility API will support compatibility data on the `Mozilla
Developer Network`_.  This currently takes the form of browser compatibility
tables, such as the one on the `CSS display property`_ page.  The API will
centralize this data, and allow it to be kept consistant across languages and
presentations.

.. _Mozilla Developer Network: https://developer.mozilla.org
.. _CSS display property: https://developer.mozilla.org/en-US/docs/Web/CSS/display#Browser_compatibility

The project started in December 2013.  The initial goals and requirements are
documented on the MozillaWiki_.

.. _MozillaWiki: https://wiki.mozilla.org/index.php?title=MDN/Projects/Development/CompatibilityTables

Status
------

The beta v1 API is being served at https://browsercompat.herokuapp.com/api/v1/.
Alpha users are using the importer_ to find and fix data issues on MDN. A small
number of pages on MDN have been converted to use API-backed compatibility
tables. Beta users can view the new tables, and non-beta users see the
traditional wiki-backed tables.  As the beta is expanded to more pages and more
users, the API is changed to handle new use cases. See the `issues page`_ for
details of planned changes.

The v1 API uses release candidate 1 (RC1) of the JSON API specification, which
was released July 2014, but is currently undocumented. See the `v1 API docs`_
for details of the API implementation.

.. _`importer`: https://browsercompat.herokuapp.com/importer
.. _`v1 API docs`: v1/intro.html
.. _`issues page`: issues.html
.. _`JSON API v1.0`: https://jsonapi.org/format/1.0/
.. _`Ember.js`: http://emberjs.com

Development
-----------

:Code:           https://github.com/mdn/browsercompat
:Server:         https://browsercompat.herokuapp.com (based on `mdn/browsercompat-data`_)
:Issues:         https://bugzilla.mozilla.org/buglist.cgi?quicksearch=compat-data (tracking bug)

                 https://bugzilla.mozilla.org/showdependencytree.cgi?id=996570&hide_resolved=1 (blocking issues for v1)
:Dev Docs:       https://browsercompat.readthedocs.org

                 https://github.com/mdn/browsercompat/wiki
:Mailing list:   https://lists.mozilla.org/listinfo/dev-mdn
:IRC:            irc://irc.mozilla.org/mdndev

.. _`mdn/browsercompat-data`: https://github.com/mdn/browsercompat-data
