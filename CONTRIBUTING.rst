============
Contributing
============

.. Note:: This project has been cancelled, and this information is historical.

Contributions should follow the `MDN Contribution Guidelines`_, and follow the
standards of this project:

* You agree to license your contributions under `MPL 2`_
* Discuss large changes on the `dev-mdn mailing list`_ or on a `bugzilla bug`_
  before coding.
* Code should follow Python and JavaScript standards.
    * Python code style should conform to `PEP8 standards`_, as well as
      `PEP257 standards`_ for documentation strings.
    * JavaScript code should follow the conventions of jslint_.
    * Code can be checked locally with ``make lint``, which must pass before
      a pull request will be considered.
* All commit messages must start with "bug NNNNNNN" or "fix bug NNNNNNN"
    * Reason: This makes it possible to read the commit log and find the bug
      that includes the original request and design conversation for all
      changes.
    * Exceptions: "Merge" and "Revert" commits
    * "fix bug NNNNNNN" - will trigger a github bot to automatically mark
      the bugzilla bug as "RESOLVED:FIXED"
    * Multiple commits are allowed, and authors are encouraged to split,
      merge, and rearrange commits in feature branches to make code review
      easier. Each commit must start with the "bug" or "fix bug" prefix.
* MDN module `owner or peer`_ must review and merge all pull requests.
    * Reason: Owner and peers are accountable for the quality of MDN code
      changes
    * Exceptions: Owners/peers may commit directly to master for critical
      security/down-time fixes; they must file a bug for follow-up review.
* MDN reviewers must verify 100% test coverage on all changes.
    * Reason: Automated tests reduce human error involved in reviews, and
      allow radical refactoring of the code.
    * Notes: The Django site has `good testing docs`_, and
      `Django REST framework`_ has some `additonal testing docs`_.
    * Coverage can be checked locally with ``make coverage``.

.. _`MDN Contribution Guidelines`: https://github.com/mozilla/kuma/blob/master/CONTRIBUTING.md
.. _`MPL 2`: http://www.mozilla.org/MPL/2.0/
.. _`dev-mdn mailing list`: https://lists.mozilla.org/listinfo/dev-mdn
.. _`bugzilla bug`: https://bugzilla.mozilla.org/show_bug.cgi?id=989448
.. _`PEP8 standards`: http://www.python.org/dev/peps/pep-0008/
.. _`PEP257 standards`: http://www.python.org/dev/peps/pep-0257/
.. _jslint:  http://www.jslint.com
.. _`owner or peer`: https://wiki.mozilla.org/Modules/All#MDN
.. _`good testing docs`: https://docs.djangoproject.com/en/dev/topics/testing/
.. _`Django REST framework`: http://www.django-rest-framework.org
.. _`additonal testing docs`: http://www.django-rest-framework.org/api-guide/testing

What to work on
---------------
There is a `tracking bug`_ for this project, and a `specific bug`_ for the data
store, the primary purpose of this project.  The dependent bugs represent
areas of work, and are not exhaustive.  If you want to contribute at this phase
in development, take a look at the bugs and linked documents, to familiarize
yourself with the project, and then get in touch with the team on IRC (#mdndev
or #browsercompat on irc.mozilla.org) to carve out a piece of the project.

.. _`tracking bug`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=989448&hide_resolved=1
.. _`specific bug`: https://bugzilla.mozilla.org/showdependencytree.cgi?id=996570&hide_resolved=1

GitHub workflow
---------------
1. `Get your environment setup`_
2. Set up mozilla remote
   (``$ git remote add mozilla git://github.com/mdn/browsercompat.git``)
3. Create a branch for a bug
   (``$ git checkout -b new-issue-888888``)
4. Develop on bug branch.

   `Time passes, the mdn/browsercompat repository accumulates new commits`
5. Commit changes to bug branch 
   (``$ git add . ; git commit -m 'fix bug 888888 - commit message'``)
6. Fetch mozilla
   (``$ git fetch mozilla``)
7. Update local master
   (``$ git checkout master; git pull mozilla master``)

   `Repeat steps 4-7 till dev is complete`

8. Rebase issue branch
   (``$ git checkout new-issue-888888; git rebase master``)
9. Push branch to GitHub
   (``$ git push origin new-issue-888888``)
10. Issue pull request (Click Pull Request button)

.. _`Get your environment setup`: installation.html

Getting translations
--------------------

Translated strings are stored in ``.po`` files in the ``locales/`` directory.

FIXME: When we set up Pontoon, add instructions here for acquiring translations.

Extracting strings
------------------

After making changes to strings that need to be translated, you need to
re-extract the strings and merge them into the translations files::

    $ ./manage.py extract
    $ ./manage.py merge

FIXME: When we set up Pontoon, add instructions here for committing all the
changes to the repository that holds the translations.
