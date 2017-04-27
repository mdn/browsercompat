Issues
======

.. Note:: This project has been cancelled, and this information is historical.

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

* **Refactor Slugs** - Slugs were designed to be human-friendly
  aliases for resources, and also to be natural key alternatives to
  auto-incrementing IDs.  However, whenever they are used for these purposes,
  they are found to have issues and require adjusting. For example, **Browser**
  slugs were adjusted to remove the "desktop by default" bias (`bug 1128525`_).
  **Feature** slugs had issues when the MDN page had a title that bumped up
  against the 50 character limit (`bug 1078699`_). Slugs will be modified to be
  changeable by privileged users, instead of being set once at creation time.
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
* **Other v1/v2 API tasks** (`tracking bug 1240757`_) - See this tracking bug
  for other issues assigned to the v1/v2 API milestone.
* **Known JSON API v1.0 issues** (`tracking bug 1243225`_) - The v2 API is a
  partial implementation of the `JSON API v1.0`_ specification. There are known
  issues around optional functionality like sorting and including linked
  resources, as well as differences in error representations. See this tracking
  bug for known issues.


Data Tasks
----------
Here are the planned tasks that involve adding or changing data in the API:

* **Add Feature IDs to MDN document data** (`bug 1240774`_) - The mechanism for including a
  Compatibility table on MDN is evolving. The latest idea is that the Feature ID
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
  This information can't be imported, and must be entered into the API.
  Some sources for this data include:

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
  modeled with HTML links.
* Support test-driven compatibility data. This is generated by browser vendors
  and standardization supporters, and can be implemented as separate
  applications using the compatibility API.

Bugzilla Archive
----------------
BrowserCompat bugs were tracked ib Bugzilla, and closed WONTFIX.  These were
the open bugs at the time the project was cancelled:

* 996570_: Create a data store for compatibility data
    * 1078699_: Resources are accessible by slug
    * 1153329_: Rename project to match browsercompat.org
    * 1159344_: Reverting a browser should attempt to revert versions order
    * 1159349_: Allow reverting deletes
        * 1229785_: No HTTP 410 error page
    * 1159363_: Add Location header to resource-creating POST responses
    * 1168455_: Add general email server to browsercompat.herokuapp.com
    * 1170214_: Limit notes to HTML subset
    * 1171988_: Restrict API actions by role
    * 1181140_: [Compat Data][Importer] Improve MDN importer, Round 3
        * 1134584_: Firefox OS 1.0.1 is not being accepted as a valid version
            * 1230584_: Improve browsable API for creating and updating resources
        * 1180573_: Standardized flag is wrong
        * 1198985_: Adjust handling of <pre> tags with brush class
    * 1195467_: A version should be unique for a browser
    * 1197210_: Allow adding new MDN feature pages
    * 1199483_: Implement Correct Labels on Chrome Browser Table
        * 1240101_: C&M GUI - display and edit browser and version
            * 1195467_: A version should be unique for a browser
    * 1219915_: [Compat] Create macros to import "requires_config" correctly
    * 1219927_: [Compat] Create macros to import "alternate_name" correctly
    * 1219945_: [Compat] Create macros to import "protected" correctly
    * 1224345_: Validation errors on view_feature become ISEs
        * 1230306_: Switch to database-independant IDs
    * 1230592_: Logging into API should return to the pre-login page
    * 1230615_: Add /Add-ons to MDN feature set
    * 1240757_: Implement v1/v2 API
        * 1195518_: upload_data tool fails with data_id collision on existing database
        * 1229170_: [stage] visiting /v1/view_features/fox causes a SystemExit exception
            * 1230584_: Improve browsable API for creating and updating resources
        * 1230306_: Switch to database-independant IDs
        * 1230584_: Improve browsable API for creating and updating resources
        * 1230597_: Add permission for changing slugs
        * 1242981_: Use instance cache for v2 API related links
        * 1251252_: Allow empty Section names
    * 1240785_: Convert required feature.slug to optional feature.aliases
        * 1230597_: Add permission for changing slugs
    * 1242606_: Some pages not re-imported by import_mdn tool
    * 1242960_: Restrict DELETE on changesets
    * 1242982_: Use instance cache for v2 relationship links
    * 1243225_: Fully implement the JSON API v1.0 specification as the v2 API
        * 1240757_: Implement v1/v2 API
        * 1242649_: Error responses should use "source" attribute, JSON Pointers
            * 1240757_: Implement v1/v2 API
        * 1242664_: Implement POST/DELETE for updating to-many relations
        * 1242703_: Pagination links are in wrong place for /api/v2/view_features/<id>?child_pages=1
        * 1242959_: v2 API should not support PUT
            * 1230584_: Improve browsable API for creating and updating resources
        * 1243190_: Support "include" parameter
        * 1243195_: Support "sort" parameter
        * 1243205_: Support updates through related links in a v2 API
        * 1243217_: Return 409 Conflict when type and id do not match URL in v2 API
        * 1252973_: Support "fields" parameter
    * 1243399_: Automate MDN data scraping
        * 1247974_: [Importer] Scrape Mozilla/Firefox_OS/API directory
    * 1244702_: C&M GUI - Provide a basic auth UI for admin
    * 1246192_: Extract localizable strings from API user interfaces

.. _`bug 1078699`: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699#c2
.. _`bug 1128525`: https://bugzilla.mozilla.org/show_bug.cgi?id=1128525
.. _`bug 1230306`: https://bugzilla.mozilla.org/show_bug.cgi?id=1230306
.. _`bug 1159349`: https://bugzilla.mozilla.org/show_bug.cgi?id=1159349
.. _`bug 1153329`: https://bugzilla.mozilla.org/show_bug.cgi?id=1153329
.. _`bug 1159406`: https://bugzilla.mozilla.org/show_bug.cgi?id=1153329
.. _`bug 1240774`: https://bugzilla.mozilla.org/show_bug.cgi?id=1240774
.. _`tracking bug 996570`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=996570&hide_resolved=1
.. _`tracking bug 1240757`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=1240757&hide_resolved=1
.. _`tracking bug 1243225`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=1243225&hide_resolved=1
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

.. _996570: https://bugzilla.mozilla.org/show_bug.cgi?id=996570
.. _1078699: https://bugzilla.mozilla.org/show_bug.cgi?id=1078699
.. _1153329: https://bugzilla.mozilla.org/show_bug.cgi?id=1153329
.. _1159344: https://bugzilla.mozilla.org/show_bug.cgi?id=1159344
.. _1159349: https://bugzilla.mozilla.org/show_bug.cgi?id=1159349
.. _1229785: https://bugzilla.mozilla.org/show_bug.cgi?id=1229785
.. _1159363: https://bugzilla.mozilla.org/show_bug.cgi?id=1159363
.. _1168455: https://bugzilla.mozilla.org/show_bug.cgi?id=1168455
.. _1170214: https://bugzilla.mozilla.org/show_bug.cgi?id=1170214
.. _1171988: https://bugzilla.mozilla.org/show_bug.cgi?id=1171988
.. _1181140: https://bugzilla.mozilla.org/show_bug.cgi?id=1181140
.. _1134584: https://bugzilla.mozilla.org/show_bug.cgi?id=1134584
.. _1230584: https://bugzilla.mozilla.org/show_bug.cgi?id=1230584
.. _1180573: https://bugzilla.mozilla.org/show_bug.cgi?id=1180573
.. _1198985: https://bugzilla.mozilla.org/show_bug.cgi?id=1198985
.. _1195467: https://bugzilla.mozilla.org/show_bug.cgi?id=1195467
.. _1197210: https://bugzilla.mozilla.org/show_bug.cgi?id=1197210
.. _1199483: https://bugzilla.mozilla.org/show_bug.cgi?id=1199483
.. _1240101: https://bugzilla.mozilla.org/show_bug.cgi?id=1240101
.. _1195467: https://bugzilla.mozilla.org/show_bug.cgi?id=1195467
.. _1219915: https://bugzilla.mozilla.org/show_bug.cgi?id=1219915
.. _1219927: https://bugzilla.mozilla.org/show_bug.cgi?id=1219927
.. _1219945: https://bugzilla.mozilla.org/show_bug.cgi?id=1219945
.. _1224345: https://bugzilla.mozilla.org/show_bug.cgi?id=1224345
.. _1230306: https://bugzilla.mozilla.org/show_bug.cgi?id=1230306
.. _1230592: https://bugzilla.mozilla.org/show_bug.cgi?id=1230592
.. _1230615: https://bugzilla.mozilla.org/show_bug.cgi?id=1230615
.. _1240757: https://bugzilla.mozilla.org/show_bug.cgi?id=1240757
.. _1195518: https://bugzilla.mozilla.org/show_bug.cgi?id=1195518
.. _1229170: https://bugzilla.mozilla.org/show_bug.cgi?id=1229170
.. _1230584: https://bugzilla.mozilla.org/show_bug.cgi?id=1230584
.. _1230306: https://bugzilla.mozilla.org/show_bug.cgi?id=1230306
.. _1230584: https://bugzilla.mozilla.org/show_bug.cgi?id=1230584
.. _1230597: https://bugzilla.mozilla.org/show_bug.cgi?id=1230597
.. _1242981: https://bugzilla.mozilla.org/show_bug.cgi?id=1242981
.. _1251252: https://bugzilla.mozilla.org/show_bug.cgi?id=1251252
.. _1240785: https://bugzilla.mozilla.org/show_bug.cgi?id=1240785
.. _1230597: https://bugzilla.mozilla.org/show_bug.cgi?id=1230597
.. _1242606: https://bugzilla.mozilla.org/show_bug.cgi?id=1242606
.. _1242960: https://bugzilla.mozilla.org/show_bug.cgi?id=1242960
.. _1242982: https://bugzilla.mozilla.org/show_bug.cgi?id=1242982
.. _1243225: https://bugzilla.mozilla.org/show_bug.cgi?id=1243225
.. _1240757: https://bugzilla.mozilla.org/show_bug.cgi?id=1240757
.. _1242649: https://bugzilla.mozilla.org/show_bug.cgi?id=1242649
.. _1240757: https://bugzilla.mozilla.org/show_bug.cgi?id=1240757
.. _1242664: https://bugzilla.mozilla.org/show_bug.cgi?id=1242664
.. _1242703: https://bugzilla.mozilla.org/show_bug.cgi?id=1242703
.. _1242959: https://bugzilla.mozilla.org/show_bug.cgi?id=1242959
.. _1230584: https://bugzilla.mozilla.org/show_bug.cgi?id=1230584
.. _1243190: https://bugzilla.mozilla.org/show_bug.cgi?id=1243190
.. _1243195: https://bugzilla.mozilla.org/show_bug.cgi?id=1243195
.. _1243205: https://bugzilla.mozilla.org/show_bug.cgi?id=1243205
.. _1243217: https://bugzilla.mozilla.org/show_bug.cgi?id=1243217
.. _1252973: https://bugzilla.mozilla.org/show_bug.cgi?id=1252973
.. _1243399: https://bugzilla.mozilla.org/show_bug.cgi?id=1243399
.. _1247974: https://bugzilla.mozilla.org/show_bug.cgi?id=1247974
.. _1244702: https://bugzilla.mozilla.org/show_bug.cgi?id=1244702
.. _1246192: https://bugzilla.mozilla.org/show_bug.cgi?id=1246192
