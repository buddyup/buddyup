#!/usr/bin/env python
import os
import json
import requests
import sys

sys.path.insert(0, os.getcwd())

from sqlalchemy import or_, and_

from buddyup.database import User, db
from buddyup import photo
from buddyup.app import app
from buddyup.util import email, delete_user


INTERCOM_API_KEY = os.environ['INTERCOM_API_KEY']
SCHOOL_NAME = os.environ.get('DOMAIN_NAME', 'buddyup-dev.herokuapp.com').split('.')[0]

def update_users():
    for user in User.query:
        if user.user_name is not None or user.email is not None:
            try:
                is_tutor = user.tutor
            except AttributeError:
                is_tutor = False

            custom_attributes = {
                'school': SCHOOL_NAME,
                'num_sent_requests': len(user.buddy_invitations_sent),
                'num_buddies': int(user.buddies.count()),
                'num_classes': int(user.courses.count()),
                'num_events_attended': int(user.events.count()),
                'has_bio': user.bio != '',
                'email_verified': user.email_verified or False,
                'is_tutor': is_tutor
            }
            
            data = {
                'custom_attributes': custom_attributes
            }
            if user.user_name:
                data['user_id'] = user.user_name
            if user.email:
                data['email'] = user.email

            headers = {'content-type': 'application/json', 'accept': 'application/json'}

            print user.email or user.user_name
            r = requests.post('https://api.intercom.io/users', data=json.dumps(data), headers=headers, auth=('5714bb0i', INTERCOM_API_KEY))
            assert r.status_code == 200

def main():
    update_users()    

if __name__ == '__main__':
    main()