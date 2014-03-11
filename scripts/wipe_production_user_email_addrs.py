#!/usr/bin/env python
'''
Modify all user email addresses to use DEFAULT_EMAIL_FORMAT instead.

** WARNING **

This is intended to be used in a development environment where you've imported 
production data.  This is destructive and will convert all user email 
addresses.

Example:
    john@smith.com ==> rbednark+john.smith.com@gmail.com
'''

import sys, os, argparse, io, logging, logging.handlers


logger = logging.getLogger('wipe_email_addrs')

sys.path.insert(0, os.getcwd())

from buddyup.app import app
from buddyup.database import db, Location, Major, Language, Course, User

parser = argparse.ArgumentParser()

EMAIL_FORMAT = app.config['DEFAULT_EMAIL_FORMAT']


def change_user_email_addrs():
    for user in User.query.all():
        user.email = None
    db.session.commit()


def warning():
    print "WARNING!  Achtung!  Attention!  Danger Will Robinson!  This command is destructive, and is only meant to be run in a dev environment in order to copy production data and then change the email addresses.  Are you sure you are in a dev environment and want to continue?"
    print "Email addresses will be converted using this format: [%s]" % EMAIL_FORMAT
    input_ = raw_input("Enter 'yes' to continue: ")
    if input_ == 'yes':
        print "Continuing..."
    else:
        sys.exit(1)


def main():
    args = parser.parse_args()
    change_user_email_addrs()


if __name__ == '__main__':
    warning()
    main()
