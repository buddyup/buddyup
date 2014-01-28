#!/usr/bin/env python
'''
Modify all user email addresses to use DEFAULT_EMAIL_FORMAT instead.
** WARNING ** : this is intended to be used in a development environment where you've imported production
data.  This is destructive and will conver all user email addresses.

Example:
    john@smith.com ==> rbednark+john.smith.com@gmail.com
'''

import sys, os, argparse, io, logging, logging.handlers


logger = logging.getLogger('wipse_email_addrs')

sys.path.insert(0, os.getcwd())

from buddyup.app import app
from buddyup.database import db, Location, Major, Language, Course, User

EMAIL_FORMAT = app.config.get("DEFAULT_EMAIL_FORMAT", 'rbednark+{user}@gmail.com')

parser = argparse.ArgumentParser()

def change_email_addr(addr):
    addr = addr.replace('@', '.')
    new = EMAIL_FORMAT.format(user=addr)
    return unicode(new)

def change_user_email_addrs():
    users = User.query.all()
    num_users = len(users)
    for num_user, user in enumerate(users):
        old = user.email
        if old:
            new = change_email_addr(addr=old)
            print "User [%s] of [%s]: changing [%s] to [%s]" % (num_user + 1, num_users, old, new)
            user.email = new
        else:
            print "  no email address for user [%s] [%s] so skipping." % (user.user_name, user.full_name)
    print "Committing..."
    db.session.commit()
    print "Done."


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
