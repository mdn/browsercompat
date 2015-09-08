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

We're defining the API and the split between API-side and client-side
functionality - see the `draft API docs`_.

.. _`draft API docs`: draft/intro.html

The next step is to implement some of the API with sample data,
as an aid to the discussion.


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
