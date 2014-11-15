#!/usr/bin/env python
import os
import hashlib
import requests
import sys

sys.path.insert(0, os.getcwd())

from sqlalchemy import or_, and_

from buddyup.database import User, db
from buddyup import photo
from buddyup.app import app
from buddyup.util import email, delete_user


def update_users():
    for user in User.query:
        if not user.email_verify_code and user.user_name:
            print "missing for %s" % user
            m = hashlib.sha1()
            m.update("Verify email for %s" % user.user_name)
            user.email_verify_code = m.hexdigest()
    
    db.session.commit()

def main():
    update_users()    

if __name__ == '__main__':
    main()