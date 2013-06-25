============
Installation
============

Inside Vagrant
==============

Vagrant automatically sets up BuddyUp via Puppet without user intervention.

Installing with Puppet
======================

Puppet is a provisioning system for Linux and some other platforms. It
automatically installs packages, creates necessary files, executes commands,
and other system administration tasks. Puppet is the recommended setup
method.

Download BuddyUp into ``/home/buddyup/buddyup``. In a root shell, run:

.. code-block:: sh

    cd /home/buddyup/buddyup
    ./scripts/setup production
    
The setup script will install Puppet, update repositories (Debian derivatives
only), and run Puppet to setup a production server. Replace ``production``
with ``dev`` to get a developer oriented system or ``test`` to get a test
oriented system.

The end result for all setups includes a virtualenv at ``/home/buddyup/venv``.
Test and production setups include an init file named ``gunicorn-buddyup`` 
with a distribution specific location. Test and dev setups include MySQL.

Manual Setup
============

System Dependencies
-------------------

* Python 2.6 or 2.7 (Usually named python)
* virtualenv (Usually python-virtualenv)

Create a user
-------------

Make a dedicated user for BuddyUp (e.g. buddyup) with a home directory (e.g.
/home/buddyup). Do not use root!

Create a virtualenv
-------------------

virtualenv is a way to create an isolated Python environment where individual
Python libraries can be installed without interfering with the system.

Pick a directory like /home/buddyup/venv for your virtualenv directory.

In a shell as the BuddyUp user, run:

.. code-block:: sh

    cd BUDDYUP_SRC_DIRECTORY
    virtualenv --distribute VIRTUALENV_DIRECTORY
    . VIRTUALENV_DIRECTORY/bin/activate
    pip -r env/requirements.txt

End result
----------

The end result is the same as a Puppet production environment