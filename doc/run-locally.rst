=======================
Running BuddyUp Locally
=======================

BuddyUp can be run locally for testing purposes.

Requirements
============

* Python 2.7 with SQLite support
* virtualenv

Pillow, the image manipulation library, has these optional requirements
that are relevant:

* libjpeg: JPEG support
* zlib: PNG support
* libtiff: TIFF support
* libwebp: Webp support



Create a virtualenv
===================

NOTE: If on Mac OS X 10.9 (Mavericks) or higher, or if running clang,
set these environment variables before continuing to prevent an issue
building the Pillow library:

	export CFLAGS=-Qunused-arguments
	export CPPFLAGS=-Qunused-arguments


In the repository, run::

    $ ./scripts/create-venv
    $ . venv/bin/activate

Create the database
===================

Running BuddyUp locally requires a SQLite database::

    $ ./scripts/create-database.py
    # Optionally, populate with default values
    $ ./scripts/populate.py all

This gives you a database at /tmp/buddyup.db. To change the location, set
the environmental variable ``DATABASE_URL``::

    $ export DATABASE_URL=sqlite:///tmp/foo.db
    $ ./scripts/create-database.py

Commands
========

When running locally with ``./runserver.py``, BuddyUp runs Flask's
built-in development server. The recommended command is::

    $ ./runserver.py --debug --reload

.. note:: If you set ``DATABASE_URL`` in the database creation stage then
    it must also be set for ``./runserver.py``.
 
This opens a fantastic debugger on exceptions and reloads the application
when modified. Reloading will end the process if there is a SyntaxError.
Also run MockCAS, a partial implementation of the CAS log in system for
testing::

    $ ./mockcas/mockcas.py -P 8000

To run in an environment that is marginally closer to production, instead
use Heroku's foreman tool, which reads from the Procfile::

    $ foreman start web

