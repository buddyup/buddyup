#!/usr/bin/env python
import os
import hashlib
import requests
import sys

sys.path.insert(0, os.getcwd())

from sqlalchemy import or_, and_

from buddyup.database import (
    db,
    User,
    Course,
    Photo,
)
from buddyup import photo
from buddyup.app import app
from buddyup.util import email, delete_user

MISLIST_SUBJECT_MAPPINGS = {
    "STATS": "STAT",
    "CALC": "MTH",
    "CHEM": "CH",
    "GEOG": "G",
    "ECON": "EC",
    "BIO": "BI",
    "PHYS": "PH",
}
COURSE_NAME_OVERIDES = {
    "CS300": "CS 300",
    "CS311": "CS 311",
}

SUBJECT_MAPPINGS = {
    "STAT": {"icon": "calculator", "name": "Statistics", },
    "MTH": {"icon": "calculator", "name": "Math", },
    "FR": {"icon": "globe", "name": "French", },
    "BI": {"icon": "paw", "name": "Biology", },
    "SPAN": {"icon": "globe", "name": "Spanish", },
    "PSY": {"icon": "lightbulb-o", "name": "Psychology", },
    "PH": {"icon": "flask", "name": "Physics", },
    "RUS": {"icon": "globe", "name": "Russian", },
    "JPN": {"icon": "globe", "name": "Japanese", },
    "MGMT": {"icon": "building", "name": "Management", },
    "AR": {"icon": "globe", "name": "Arabic", },
    "ANTH": {"icon": "university", "name": "Anthropology", },
    "CH": {"icon": "flask", "name": "Chemistry", },
    "COMM": {"icon": "film", "name": "Communication", },
    "CR": {"icon": "lightbulb-o", "name": "Conflict Resolution", },
    "EC": {"icon": "building", "name": "Economics", },
    "ENG": {"icon": "pencil", "name": "English", },
    "ESM": {"icon": "pencil", "name": "Environmental Science & Management", },
    "G": {"icon": "globe", "name": "Geology", },
    "HST": {"icon": "university", "name": "History", },
    "INTL": {"icon": "globe", "name": "International Studies", },
    "LING": {"icon": "pencil", "name": "Applied Linguistics", },
    "PHL": {"icon": "lightbulb-o", "name": "Philosophy", },
    "SOC": {"icon": "lightbulb-o", "name": "Sociology", },
    "SPHR": {"icon": "lightbulb-o", "name": "Speech & Hearing Science", },
    "WLL": {"icon": "globe", "name": "World Languages & Literatures", },
    "CS": {"icon": "calculator", "name": "Computer Science", },
    "ECE": {"icon": "calculator", "name": "Electrical and Computer Engineering", },
    "MUS": {"icon": "paint", "name": "Music", },
}

# flask
# calculator
# university
# globe
# paint
# building
# pencil
# cutlery
# film
# paw
# lightbulb-o
# medkit

IGNORE_SUBJECT_LIST = [
    "OTHER",
    "Group Theory"
]


def import_data():
    tng_id = os.environ["TNG_ID"]
    print("Migrating for %s" % tng_id)

    courses = []
    students = []
    subjects = {}


    print("Migrating courses..")
    for course in Course.query:
        try:
            if course.name not in IGNORE_SUBJECT_LIST:
                if course.name in COURSE_NAME_OVERIDES:
                    name = COURSE_NAME_OVERIDES[course.name]
                else:
                    name = course.name
                subject, code = name.split(" ")

                if subject in MISLIST_SUBJECT_MAPPINGS:
                    subject = MISLIST_SUBJECT_MAPPINGS[subject]

                if not subject.upper() in SUBJECT_MAPPINGS:
                    raise Exception("Unknown subject %s from %s" % (subject, name))

        except Exception, e:
            print "Error parsing %s" % course.name
            raise

        # name = db.Column(db.UnicodeText)
        # instructor = db.Column(db.UnicodeText)
        # events = db.relationship('Event', backref='course')

# class_obj = {
#     "id": "-JuiQ4-yYIbfCqI0CZmQ",
#     "profile": {
#         "code": "1602",
#         "id": "-JuiQ4-yYIbfCqI0CZmQ",
#         "name": "Introduction to Gender Studies",
#         "school_id": "sydney_edu_au",
#         "subject_code": "GCST",
#         "subject_icon": "pencil",
#         "subject_name": "Gender and Cultural Studies"
#     }
# }
    print("Migrating users..")
    for user in User.query:
        print(user)
    #     user_obj = {
    #         "classes": {
    #             "-JuhlLFxoYvaivUl5Les": {
    #                 "code": "1101",
    #                 "course_id": "-JuhlLFxoYvaivUl5Les",
    #                 "id": "-JuhlLFxoYvaivUl5Les",
    #                 "name": "Chemistry 1A",
    #                 "school_id": "%s" % tng_id,
    #                 "subject_code": "CHEM",
    #                 "subject_icon": "flask",
    #                 "subject_name": "Chemistry"
    #             }
    #         },

    #         "pictures": {
    #             "original": "data:image/png;base64,iVBORw0KGgoAAA"
    #         },
    #         "private": {
    #             "badge_count": 0,
    #             "email_buddy_request": "on",
    #             "email_groups": "everyone",
    #             "email_hearts": "buddies",
    #             "email_my_groups": "on",
    #             "email_private_message": "on",
    #             "push_buddy_request": "on",
    #             "push_groups": "everyone",
    #             "push_hearts": "everyone",
    #             "push_my_groups": "on",
    #             "push_private_message": "on"
    #         },
    #         "public": {
    #             "bio": "Me! Rabbits.",
    #             "buid": "-Jutvurlo6atQliTl27u",
    #             "first_name": "Sharon",
    #             "last_name": "Kitching",
    #             "profile_pic_url_medium": "https://buddyup-core.s3.amazonaws.com:443/profile_pics/9fda1979630b061c3fbb46a39551bb3eaa41b34c-medium.jpg",
    #             "profile_pic_url_tiny": "https://buddyup-core.s3.amazonaws.com:443/profile_pics/9fda1979630b061c3fbb46a39551bb3eaa41b34c-tiny.jpg",
    #             "signed_up_at": 1437638569000
    #         },
    #         "schools": {
    #             "%s" % tng_id: {
    #                 "id": "%s" % tng_id,
    #                 "name": "University of Sydney"
    #             }
    #         }
    #     }


    # id = db.Column(db.Integer, primary_key=True)
    # created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    # # Note: Portland State University user names are always <= 8 ASCII characters
    # user_name = db.Column(db.String(255), index=True, unique=True)
    # full_name = db.Column(db.UnicodeText, default=u"")
    # bio = db.Column(db.UnicodeText, default=u"")
    # facebook = db.Column(db.UnicodeText, default=u"")
    # facebook_token = db.Column(db.UnicodeText)
    # twitter = db.Column(db.UnicodeText, default=u"")
    # twitter_token = db.Column(db.UnicodeText)
    # twitter_secret = db.Column(db.UnicodeText)
    # linkedin = db.Column(db.UnicodeText, default=u"")
    # skype = db.Column(db.UnicodeText, default=u"")
    # linkedin_token = db.Column(db.UnicodeText)
    # google_token = db.Column(db.UnicodeText)
    # location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    # email = db.Column(db.UnicodeText)
    # has_photos = db.Column(db.Boolean, default=False)
    # email_verified = db.Column(db.Boolean, default=False)
    # email_verify_code = db.Column(db.UnicodeText, default=u"")
    # #tutor = db.Column(db.Boolean, default = False)

    # # Initialized flag
    # initialized = db.Column(db.Boolean, default=False)
    
    # def __repr__(self):
    #     return '%s' % self.full_name

    # # Relationships
    # location = db.relationship('Location')
    # courses = db.relationship('Course',
    #                           secondary=CourseMembership,
    #                           backref=db.backref('users', lazy="dynamic"),
    #                           lazy='dynamic')
    # archived_courses = db.relationship('Course',
    #                           secondary=ArchivedCourseMembership,
    #                           lazy='dynamic')

    # majors = db.relationship('Major', lazy="dynamic",
    #                          secondary=MajorMembership,
    #                          backref='users')
    # languages = db.relationship('Language', lazy='dynamic',
    #                             secondary=LanguageMembership,
    #                             backref=db.backref('users', lazy="dynamic"))
    # notifications = db.relationship('Notification', backref='recipient',
    #                             primaryjoin=Notification.recipient_id == id)

    # notifications_sent = db.relationship('Notification', backref='sender',
    #                             primaryjoin=Notification.sender_id == id)

    # buddies = db.relationship('User', secondary=Buddy,
    #                           lazy='dynamic',
    #                           primaryjoin=Buddy.c.user1_id == id,
    #                           secondaryjoin=Buddy.c.user2_id == id)
    # buddy_invitations_sent = db.relationship('BuddyInvitation', backref='sender',
    #                             primaryjoin=BuddyInvitation.sender_id == id)
    # buddy_invitations_received = db.relationship('BuddyInvitation', backref='receiver',
    #                             primaryjoin=BuddyInvitation.receiver_id==id)

    # events = db.relationship('Event', lazy="dynamic",
    #                          primaryjoin=EventMembership.c.user_id==id,
    #                          secondary=EventMembership,
    #                          backref=db.backref('users', lazy="dynamic"))
    # event_invitations_sent = db.relationship('EventInvitation', backref='sender',
    #                             primaryjoin=EventInvitation.sender_id==id)
    # event_invitations_received = db.relationship('EventInvitation', backref='receiver',
    #                             primaryjoin=EventInvitation.receiver_id==id,
    #                             lazy="dynamic")

    print("Saving School...")
    # {
    #     "classes": {
    #         "-JuhlLFxoYvaivUl5Les": {
    #             "code": "1101",
    #             "id": "-JuhlLFxoYvaivUl5Les",
    #             "name": "Chemistry 1A",
    #             "school_id": "sydney_edu_au",
    #             "subject_code": "CHEM",
    #             "subject_icon": "flask",
    #             "subject_name": "Chemistry"
    #         },
    #         "-JuhlfJ368zjSoPUdUqT": {
    #             "code": "1003",
    #             "id": "-JuhlfJ368zjSoPUdUqT",
    #             "name": "Physics 1 (Technological)",
    #             "school_id": "sydney_edu_au",
    #             "subject_code": "PHYS",
    #             "subject_icon": "lightbulb-o",
    #             "subject_name": "Physics"
    #         },
    #         "-JuiQ4-yYIbfCqI0CZmQ": {
    #             "code": "1602",
    #             "id": "-JuiQ4-yYIbfCqI0CZmQ",
    #             "name": "Introduction to Gender Studies",
    #             "school_id": "sydney_edu_au",
    #             "subject_code": "GCST",
    #             "subject_icon": "pencil",
    #             "subject_name": "Gender and Cultural Studies"
    #         },
    #         "-JuiQRSX5zZkKFeOEm6w": {
    #             "code": "1002",
    #             "id": "-JuiQRSX5zZkKFeOEm6w",
    #             "name": "Introductory Macroeconomics",
    #             "school_id": "sydney_edu_au",
    #             "subject_code": "ECON",
    #             "subject_icon": "globe",
    #             "subject_name": "Economics"
    #         }
    #     },
    #     "profile": {
    #         "active": true,
    #         "city": "Sydney",
    #         "email_suffix": "sydney.edu.au",
    #         "id": "sydney_edu_au",
    #         "logo_full_url": "",
    #         "logo_lg_url": "",
    #         "logo_md_url": "",
    #         "logo_sm_url": "",
    #         "name": "University of Sydney",
    #         "primary_color": "blue",
    #         "secondary_color": "green",
    #         "short_name": "Sydney Uni",
    #         "state": "Australia",
    #         "web_site": "sydney.edu.au",
    #         "website": "http://sydney.edu.au/"
    #     },
    #     "students": {
    #         "-JuhimjeBisoiUPmf4XA": true,
    #         "-JujFeNUwxfSZlUQAz_f": true,
    #         "-Jutvurlo6atQliTl27u": true,
    #         "-JvCYmctaxKivki7nbqV": true,
    #         "-JvHtSiLmrT16Ox2vqvu": true
    #     },
    #     "subjects": {
    #         "CHEM": {
    #             "code": "CHEM",
    #             "icon": "flask",
    #             "name": "Chemistry"
    #         },
    #         "ECON": {
    #             "code": "ECON",
    #             "icon": "globe",
    #             "name": "Economics"
    #         },
    #         "GCST": {
    #             "code": "GCST",
    #             "icon": "pencil",
    #             "name": "Gender and Cultural Studies"
    #         },
    #         "PHYS": {
    #             "code": "PHYS",
    #             "icon": "lightbulb-o",
    #             "name": "Physics"
    #         }
    #     }
    # }

    # db.session.commit()


def main():
    import_data()    

if __name__ == '__main__':
    main()
