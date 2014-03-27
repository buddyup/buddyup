~~~~~~~~~~~~~~~
Utility Scripts
~~~~~~~~~~~~~~~

Various utility scripts are located in scripts/

compile-svg.sh
==============

Usage: ./scripts/svg-compile.sh

compile-svg.sh grabs SVG files from buddyup/svg/, compiles them to a given
size as a PNG, and writes them to buddyup/static/img/ in the format
{name}-{x}-{y}.png.

Dependencies: rsvg


svg-compile.sh should be run locally

create-database.py
==================

Create all tables in the current DATABASE_URL. Must have a virtualenv
activated. Just uses SQLAlchemy's create_all()

Usage: ./scripts/create-database.py

create-venv
===========

Usage: ./scripts/create-venv

Create a virtualenv in the current working directory called venv/

drop-database.py
================

The opposite of create-database.py

Usage: ./scripts/create-database.py

dump-defaults.py
================

Dump files from the database for default values for some tables (majors,
languages, etc.). Can be restored with `populate.py`_. Output should usually
be stored in defaults/

::

    usage: populate.py [-h] [--clear] [--verbose] [--list-targets]
                    [targets [targets ...]]

    positional arguments:
    targets             Targets to load. 'all' loads all available targets

    optional arguments:
    -h, --help          show this help message and exit
    --clear, -c         Clear old records
    --verbose, -v       Print while you insert!
    --list-targets, -l  List populate targets
  
photos
======

Query and manipulate photos. Subcommands::

    clear               clear a user's photos
    upload              upload a photo for a user
    download            download photos for a user
    list                list users with photos
    has-photos          Test for user having a photo
    transfer            transfer from another s3 bucket

See help for each subcommand::

    $ ./scripts/photos {subcommand} -h

populate.py
===========

Load the dumped values from `dump-defaults.py`_ that are placed in defaults/

::

    usage: populate.py [-h] [--clear] [--verbose] [--list-targets]
                    [targets [targets ...]]

    positional arguments:
    targets

    optional arguments:
    --clear, -c         Clear old records
    --verbose, -v       Print while you insert!
    --list-targets, -l  List populate targets

    
