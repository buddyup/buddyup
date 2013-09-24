=================
Development Notes
=================

Concurrency
===========

In production, BuddyUp uses gevent to provide concurrency. That allows BuddyUp
to make connections that look blocking (e.g. urllib2 and Amazon S3 via boto),
but actually only pause a lightweight green thread. The server that sits in
front of Flask, gunicorn (lowercase), is configured to use 3 worker processes.
See Procfile in the top of the repository.

Python 3
========

These dependencies are not ported as of September 20, 2013:

boto, the Amazon services library, has a port in progress.

Flask-SQLAlchemy is not ported and does not have an open issue for Python 3
support. However, the repository is owned by mitsuhiku, Flask's lead
developer, so it should be ported soon.

flask-heroku only requires some very simple fixes. I have a pull request in
place on GitHub, but it has not been accepted. My own repository is at::

    https://github.com/adevore/flask-heroku

When these dependencies are ported, the minimum Python 3 requirement will be
Python 3.3. As part of porting, make sure to remove anything from
requirements.txt that is irrelevant. BuddyUp was written with Python 3
migration in mind, so porting should be limited to a 2to3 

PyPy
====

In the case of CPU time being a bottleneck, PyPy is one option to explore.
The only incompatible dependency is psycopg2. There is a ctypes based
implementation called psycopg2ct that works on both CPython 2 and PyPy.
Scaling up to multiple dynos on Heroku is an easier route.

Flask-Runner
============

Flask-Runner is fetched directly from GitHub (see requirements.txt). The
developer of Flask-Runner made some changes that broke running the debugger
for me, then deleted the old version from the Python Package Index.