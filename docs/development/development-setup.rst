=================
Development setup
=================

Development environment & unit tests
------------------------------------

The basic method to set up a local environment is::

    mkvirtualenv -p `which python3` irrd
    pip install -r requirements.txt

Some of the test use a live database for thoroughness. The database
URL needs to be set in ``IRRD_DATABASE_URL``, e.g. for a local database,
no authentication, database ``irrd_test``::

    export IRRD_DATABASE_URL=postgresql:///irrd_test

The tests will refuse to work on a database that already has tables.
Note that setting this environment variable will also override the database
for running IRRd itself.

To run the tests with py.test, you can simply run::

    pytest irrd

If you'd also like to measure coverage and see missing lines, run it as::

    pytest --cov-report term-missing --cov=irrd irrd

If you're running the tests on Mac OS X, there is an issue where default
temporary directories have names too long for GnuPG, causing a 5-second delay.
To avoid this, use ``--basetemp`` to set an alternate temporary directory, e.g.::

    pytest --cov-report term-missing --cov=irrd --basetemp=.tmpdirs/ irrd

You may also want to add ``-v`` for more verbose output.

Integration test
----------------

The integration test is not included when running ``pytest irrd``.
To run the integration test, two databases need to be configured, e.g.::

    export IRRD_DATABASE_URL_INTEGRATION_1=postgresql:///irrd_test1
    export IRRD_DATABASE_URL_INTEGRATION_2=postgresql:///irrd_test2

.. danger::
    The integration test will wipe all contents of IRRd tables in the databases
    ``IRRD_DATABASE_URL_INTEGRATION_1`` and ``IRRD_DATABASE_URL_INTEGRATION_2``
    without further checks or confirmation.

The test can then be started with::

    pytest --basetemp=.tmpdirs/ -s -vv irrd/integration_tests/run.py

The `-s` parameter prevents `stdout` capture (i.e. shows stdout output in the
console), which gives some information about the test setup to aid in
debugging. This example also uses the temporary directory name fix for
Mac OS X, as suggested for unit tests.

The integration test will start two instances of IRRd, one mirroring off the
other, and an email server that captures all mail. It will then run a series
of updates and queries, verify the contents of mails, the state of the
databases, mirroring, utf-8 handling and run all basic types of queries.

Code coverage is not measured for the integration test, as its purpose is
not to test all paths, but rather verify that the most important paths
are working end-to-end.

Mypy and flake8
---------------

In addition to the tests, this project uses `mypy` for type checking and `flake8`
for style checking. To run these, run::

    mypy irrd --ignore-missing-imports
    flake8

If all is well, neither command should provide output.

Exclusions from checks
----------------------

Code can be excluded from code coverage, and can be excluded from checks by
`mypy` and `flake8`. This should be done in rare cases, where the quality of
the code would suffer otherwise, and for tests where the risks are small and
the effort would be great.

To ignore a line or block for test coverage, add ``# pragma: no cover`` to
the end, ``# type:ignore`` to ignore `mypy` errors, and ``# noqa: <number>``
for `flake8` violations. For the latter, the number is the error number
from the command output.

Docs
----

The documentation is written in reStructuredText, and an HTML version
can be generated with::

    cd docs
    make html
    open _build/html/index.html

If you're new to the RST format, you may find the `quick reference`_ helpful.

.. _quick reference: http://docutils.sourceforge.net/docs/user/rst/quickref.html

Making a release
----------------
To create a new packaged version of IRRD:

* Create the new release notes and commit them in the master branch.
* If this is a new minor release (x.y), create a new branch for it first - otherwise
  switch to the branch of the current minor release.
* Cherry-pick the changes from the master branch, at least including the release
  notes commit. Version updates of dependencies are not generally applied to
  the release branch, except in case of known important bugs or security issues.
* Ensure the version is correct/updated in ``irrd/__init__.py``.
* Commit the version change.
* Tag the new release with git (`git tag -a <tagname>`),
  and push the tag (`git push origin <tag_name>`).
* Run ``./setup.py sdist bdist_wheel``
* Your source archive and built distribution are now in ``dist/``
* Upload them to PyPI with ``twine upload dist/*``

For more background, a good start is the `Python packaging tutorial`_.

.. _Python packaging tutorial: https://packaging.python.org/tutorials/packaging-projects/
