Issues
======
The near-term goal is that compatibility data lives in the API rather than on
the MDN page, and MDN contributors maintain this data in the API instead of
editing wiki pages. As this plan is executed, limitations are discovered in
API, and changes are made and deployed.

When MDN is using the API as the primary source of compatibility data, we'll
increment the API version for backward-incompatible changes. Until then, the
v1 and v2 APIs will be modified with the evolving design.

This page outlines planned changes in the API. It doesn't describe all the
known bugs and issues - see `tracking bug 996570`_ for a detailed list.

API Tasks
---------
Here are the planned tasks that will require code changes to the API:

* **Implement v2 API** (`bug 1159406`_) - `JSON API v1.0`_ was released May
  2015, and is quite different from JSON API Release Candidate 1 (RC1), which
  was used to design the v1 API. Many libraries in many languages support JSON
  API v1.0, including Ember 2.0, released August 2015. JSON API v1.0 will be
  supported in the v2 API, and both v1 and v2 will be supported until tools
  have been migrated to the v2 API.
* **Refactor Slugs** - Slugs were designed to be human-friendly
  aliases for resources, and also to be natural key alternatives to
  auto-incrementing IDs.  However, whenever they are used for these purposes,
  they are found to have issues and require adjusting. For example, **Browser**
  slugs were adjusted to remove the "desktop by default" bias (`bug 1128525`_).
  **Feature** slugs had issues when the MDN page had a title that bumped up
  against the 50 character limit (`bug 1078699`_). Slugs will be modified to be
  changable by privileged users, instead of being set once at creation time.
  They may also be expanded beyond 50 characters, become a list of optional
  aliases, and be renamed in some cases. 3rd party developers should not rely
  on slugs remaining constant for the life of the API.
* **Switch from Auto-Incrementing IDs to UUIDs** (`bug 1230306`_) - Resources
  are accessed by IDs, which using the database's auto-incrementing integers.
  This means that two instances of the API could have the same data available
  at different IDs.  Tools currently use slugs and other "permanent" attributes
  to identify resources as the same, even when IDs change. This is error-prone,
  and since slugs are planned to change, it would be useful to use UUIDs
  instead, so that the ID becomes a strong identifier between API instances.
* **Recover deleted items** (`bug 1159349`_) - The History API could be used to
  recover deleted items, by administrators or users. The API needs to be
  modified to allow the reversion PATCH to deleted resources.
* **Move to api.browsercompat.org** (`bug 1153329`_) -
  https://browsercompat.org will be the user-facing contribution interface and
  data browser.  https://api.browsercompat.org will be the application-facing
  interface. This may require renaming the github repository, moving paths, and
  dropping sample views.

Data Tasks
----------
Here are the planned tasks that involve adding or changing data in the API:

* **Add Feature IDs to MDN document data** - The mechanism for including a
  Compatiblity table on MDN is evolving. The latest idea is that the Feature ID
  will be stored in the MDN document model, so that the existing parameterless
  KumaScript can used to inject the table. There are open design questions,
  such as how the IDs will be set, if they need to change, and, if so, who
  will change them and how.
* **Import Data from MDN** - The majority of the project work has been building
  a scraper capable of importing existing data from MDN. As of September 2015,
  the scraper can extract data from most MDN pages, and can pinpoint issues
  that require page changes. The scraped data has to be committed to the API,
  and this process is ongoing.
* **Populate Browser Version Data** - MDN has detailed information for Firefox
  releases, and much less for other browsers.  The **version** model supports
  some data, such as a release date, a retirement date, and URLs for release
  notes.  Versions can also be sorted with respect to the related **browser**.
  This information can't be importea release date and a retirement date, as
  well as other version data. Some sources for this data include:

    * Google Chrome - `Google Chrome Release History`_ on Wikipedia
    * Mozilla Firefox - `Firefox Release History`_ on Wikipedia and KumaScript
      macro CompatGeckoDesktop_
    * Microsoft Internet Explorer - `Release History of IE`_ on Wikipedia
    * Opera - `Current Opera version history`_ and `Presto history`_ on opera.com
    * Safari - `Safari version history`_ on Wikipedia

Future Tasks
------------
Once MDN is using the API as the primary data source for compatibility data,
we can move on to other goals.

This includes, but is not limited to:

* Supporting other relations between resources. For example, the CSS property
  ``color`` can be assigned a CSS color type such as ``color=red``. The CSS
  property ``background-color`` can also be assigned CSS color types.
  Different browsers may support a different set of named colors. This
  relation can't be directly represented in the API, but can be partially
  modelled with HTML links.
* Support test-driven compatibility data. This is generated by browser vendors
  and standardization supporters, and can be implemented as separate
  applications using the compatibility API.

.. _`bug 1078699`: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699#c2
.. _`bug 1128525`: https://bugzilla.mozilla.org/show_bug.cgi?id=1128525
.. _`bug 1230306`: https://bugzilla.mozilla.org/show_bug.cgi?id=1230306
.. _`bug 1159349`: https://bugzilla.mozilla.org/show_bug.cgi?id=1159349
.. _`bug 1153329`: https://bugzilla.mozilla.org/show_bug.cgi?id=1153329
.. _`bug 1159406`: https://bugzilla.mozilla.org/show_bug.cgi?id=1153329
.. _`tracking bug 996570`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=996570&hide_resolved=1
.. _CompatGeckoDesktop: https://developer.mozilla.org/en-US/docs/Template:CompatGeckoDesktop
.. _`Browser Compatibility Data Architecture`: https://docs.google.com/document/d/1YF7GJ6kgV5_hx6SJjyrgunqznQU1mKxp5FaLAEzMDl4/edit#
.. _`Chrome release history`: http://en.wikipedia.org/wiki/Google_Chrome_complete_version_history#Release_history
.. _`Current Opera version history`: http://www.opera.com/docs/history/
.. _`Firefox release history`: http://en.wikipedia.org/wiki/Firefox_release_history#Release_history
.. _`Google Chrome Release History`: http://en.wikipedia.org/wiki/Google_Chrome#Release_history
.. _`JSON API v1.0`: https://jsonapi.org/format/1.0/
.. _`Presto history`: http://www.opera.com/docs/history/presto/
.. _`Release History of IE`: http://en.wikipedia.org/wiki/Internet_Explorer_1#Release_history_for_desktop_Windows_OS_version
.. _`Safari version history`: http://en.wikipedia.org/wiki/Safari_version_history#Release_history
