Register for a Heroku Account
=============================

Create an SSH key
=================

Run in a terminal::

    ssh-keygen -f ~/.ssh/id_rsa

Install Heroku Toolbelt
=======================

See: https://devcenter.heroku.com/articles/heroku-command

Follow the instructions for installing and logging in.

Setting Up An App
=================

Pick a name for the app (e.g. buddyup). The app will be accessible via
app-name.herokuapp.com. Run::

    cd <git repository>
    heroku create <app name>
    git push heroku master
    

Deploy Using Git
================

Run::

    cd <git repository>
    git push heroku master

This command will upload your repository to Heroku and create a "slug"
on Heroku's servers.

Add Heroku Postgres
===================

Provision Heroku's Postgres addon::

    cd <git repository>
    heroku addons:add heroku-postgresql:<postgres plan>

Where ``<postgres plan>`` is the name of your desired postgres plan.
Developers should use the ``dev`` plan.

Next create the database::

    heroku run init

Mail
====

Mail alerts are not implemented yet.

Amazon S3
=========

Create a bucket