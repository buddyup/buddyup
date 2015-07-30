#!/usr/bin/env python
import csv
import os
import json
import hashlib
import requests
import re
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
    "MGNT": "MGMT",
    "SPA": "SPAN",
    "CHEN": "CH",
    "MA": "MTH",
    "MATH": "MTH",
    "MNGMT": "MGMT",
}
COURSE_NAME_OVERIDES = {
    "CS300": "CS 300",
    "CS311": "CS 311",
    "PS 399 - 002": "PS 399",
    "STATS 244 FLIGHT": "STATS 244",
    "STATS 243 WEBB": "STATS 243",
    "CH-221": "CH 221",
    "BI 252 BALLHORN": "BI 252",
    "STATS 243 BLACKMORE": "STATS 243",
    "STAT 243 BLACKMORE": "STAT 243",
    "STATS 243 BLACKMORE": "STATS 243",
    "STATS244 BLACKMORE": "STATS 244",
    "PSY 350 LANDES": "PSY 350",
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
    "MUS": {"icon": "paint-brush", "name": "Music", },
    "WR": {"icon": "pencil", "name": "Writing", },
    "KOR": {"icon": "globe", "name": "Korean", },
    "ART": {"icon": "paint-brush", "name": "Art", },
    "ASL": {"icon": "globe", "name": "American Sign Language", },
    "CHN": {"icon": "globe", "name": "Chinese", },
    "BST": {"icon": "globe", "name": "Black Studies", },
    "PHE": {"icon": "medkit", "name": "Public Health Education", },
    "EAS": {"icon": "calculator", "name": "Engineering and Applied Sciences", },
    "ARH": {"icon": "paint-brush", "name": "Art History", },
    "UNST": {"icon": "university", "name": "University Studies", },
    "BA": {"icon": "building", "name": "Business Administration", },
    "MKTG": {"icon": "building", "name": "Marketing", },
    "WS": {"icon": "globe", "name": "Women's Studies", },
    "CE": {"icon": "calculator", "name": "Civil Engineering", },
    "GER": {"icon": "globe", "name": "German", },
    "ACTG": {"icon": "building", "name": "Accounting", },
    "SYSC": {"icon": "lightbulb-o", "name": "Systems Science", },
    "LAT": {"icon": "university", "name": "Latin", },
    "CHLA": {"icon": "globe", "name": "Chicano-Latino", },
    "FILM": {"icon": "film", "name": "Film", },
    "PS": {"icon": "university", "name": "Political Science", },
    "PE": {"icon": "medkit", "name": "Physical Education", },
    "SPED": {"icon": "lightbulb-o", "name": "Special Education", },
    "HON": {"icon": "lightbulb-o", "name": "Honors", },
}

SCHOOL_NAME = {
    "pdx_edu": "Portland State University",
    "buddyup_org": "BuddyUp University",
    "oregonstate_edu": "Oregon State University",
    "oit_edu": "Oregon Institute of Technology",
    "oregonstate_edu": "Oregon State University",
    "smccd_edu": "San Mateo Community College District",
    "stanford_edu": "Stanford",
    "sydney_edu_au": "University of Sydney",
}

# flask
# calculator
# university
# globe
# paint-brush
# building
# pencil
# cutlery
# film
# paw
# lightbulb-o
# medkit

IGNORE_SUBJECT_LIST = [
    "OTHER",
    "Group Theory",
    "421-526",
]

tng_id = os.environ["TNG_ID"]


CLASS_NAME_MAPPING = {}

if tng_id == "buddyup_org" or tng_id == "pdx_edu":
    with open('scripts/psu_fall_2014.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0]:
                CLASS_NAME_MAPPING[row[0]] = row[3].title()


def get_class_name(subject, code):
    name = "%s %s" % (subject, code)
    if name in CLASS_NAME_MAPPING:
        return CLASS_NAME_MAPPING[name]
    return name


def firebase_url(endpoint):
    if not endpoint.endswith("/"):
        endpoint = "%s/" % endpoint
    if endpoint.startswith("/"):
        endpoint = endpoint[1:]

    return "https://%s/%s.json?format=export&auth=%s" % (
        os.environ["FIREBASE_ENDPOINT"],
        endpoint,
        os.environ["FIREBASE_KEY"],
    )


def firebase_put(endpoint, data, acks_late=True):
    # TODO: get endpoint make sure it hasn't been updated more recently.
    # print(firebase_url(endpoint))
    r = requests.put(firebase_url(endpoint), json.dumps(data))
    if not r.status_code == 200:
        print(r.status_code)
        print(r.json())
    assert r.status_code == 200


def firebase_patch(endpoint, data, acks_late=True):
    r = requests.patch(firebase_url(endpoint), json.dumps(data))
    if not r.status_code == 200:
        print(r.status_code)
        print(r.json())
    assert r.status_code == 200


def firebase_post(endpoint, data, acks_late=True):
    r = requests.post(firebase_url(endpoint), json.dumps(data))
    if not r.status_code == 200:
        print(r.status_code)
        print(r.json())
    assert r.status_code == 200
    return r.json()


def firebase_get(endpoint, acks_late=True):
    # r = requests.get(firebase_url(endpoint), json.dumps(data))
    r = requests.get(firebase_url(endpoint))
    if not r.status_code == 200:
        print(r.status_code)
        print(r.json())
    assert r.status_code == 200
    return r.json()


def import_data():
    print("Migrating for %s" % tng_id)

    courses = {}
    students = []
    subjects = {}
    CLASSES_BY_PK = {}
    student_data = {}


    print("Parsing courses..")
    for course in Course.query:
        parsing_error = False
        if course.name.strip() not in IGNORE_SUBJECT_LIST:
            try:
                if course.name.strip() in COURSE_NAME_OVERIDES:
                    name = COURSE_NAME_OVERIDES[course.name.strip()]
                else:
                    name = course.name.strip()

                if " " not in name:
                    split = re.split('(\d+)', name)
                    name = "%s %s" % (split[0], ''.join(split[1:]))
                subject, code = name.split(" ")

                if subject in MISLIST_SUBJECT_MAPPINGS:
                    subject = MISLIST_SUBJECT_MAPPINGS[subject]

                if subject.upper() not in SUBJECT_MAPPINGS:
                    raise Exception("Unknown subject %s from %s" % (subject, name))

            except Exception, e:
                # print "Error parsing %s" % name
                parsing_error = True
                # raise

            courses[course.id] = {
                "name": name,
                "subject": subject,
                "code": code,
                "students": [],
                "parsing_error": parsing_error
            }
            if not parsing_error:
                subjects[subject] = {
                    "name": SUBJECT_MAPPINGS[subject]["name"],
                    "icon": SUBJECT_MAPPINGS[subject]["icon"],
                    "code": subject,
                    "parsing_error": parsing_error
                }
                courses[course.id]["icon"] = SUBJECT_MAPPINGS[subject.upper()]["icon"]
                courses[course.id]["subject_name"] = SUBJECT_MAPPINGS[subject.upper()]["name"]

    print("Parsing users..")
    for user in User.query:
        # print(user)
        for c in user.courses:
            if c.id in courses:
                courses[c.id]["students"].append(user.id)
            # print(c.id)
        students.append(user)

    print("Saving school...")
    firebase_patch("/schools/%s/profile" % tng_id, {
        "active": True,
    })
    firebase_classes = firebase_get("/schools/%s/classes" % tng_id)

    firebase_subjects = firebase_get("/schools/%s/subjects" % tng_id)

    print("Saving subjects...")
    for id, s in subjects.items():
        if s["code"] not in firebase_subjects:
            print("Adding %s - %s" % (s["code"], s["name"]))
            data = {
                "code": s["code"],
                "icon": s["icon"],
                "name": s["name"],
            }
            firebase_patch("schools/%s/subjects/%s/" % (tng_id, s["code"]), data)
        else:
            print("Exists %s - %s" % (s["code"], s["name"]))

    print("Saving courses...")
    for db_pk, c in courses.items():
        # print "%s: %s" % (c["name"], len(c["students"]))
        if len(c["students"]) > 1:
            if c["parsing_error"]:
                # raise Exception("Error parsing %s" % (c["name"]))
                print("Error parsing %s" % (c["name"]))
            else:
                found = False
                if firebase_classes:
                    for key, data in firebase_classes.items():
                        if (
                            c["subject"] == data["subject_code"] and
                            c["code"] == data["code"]
                        ):
                            found = True
                            c["id"] = key
                            break

                if not found:
                    print("Adding %s %s - %s" % (c["subject"], c["code"], get_class_name(c["subject"], c["code"])))
                    data = {
                        "profile": {
                            "code": c["code"],
                            "name": get_class_name(c["subject"], c["code"]),
                            "school_id": tng_id,
                            "subject_code": c["subject"],
                            "subject_icon": c["icon"],
                            "subject_name": c["subject_name"],
                        }
                    }
                    # print(data)
                    resp = firebase_post("classes/", data)
                    print(resp)
                    id = resp["name"]
                    c["id"] = id
                    firebase_patch("classes/%s/" % id, {"id": id})
                    firebase_patch("classes/%s/profile/" % id, {"id": id})

                    firebase_patch("schools/%s/classes/%s/" % (tng_id, id), {
                        "code": data["profile"]["code"],
                        "id": id,
                        "name": get_class_name(c["subject"], c["code"]),
                        "school_id": tng_id,
                        "subject_code": data["profile"]["subject_code"],
                        "subject_icon": data["profile"]["subject_icon"],
                        "subject_name": data["profile"]["subject_name"],
                    })

                else:
                    print("Exists: %s %s" % (c["subject"], c["code"],))

                CLASSES_BY_PK["%s" % db_pk] = {
                    "code": c["code"],
                    "id": c["id"],
                    "name": get_class_name(c["subject"], c["code"]),
                    "school_id": tng_id,
                    "subject_code": c["subject"],
                    "subject_icon": c["icon"],
                    "subject_name": c["subject_name"],
                }

        # name = db.Column(db.UnicodeText)
        # instructor = db.Column(db.UnicodeText)
        # events = db.relationship('Event', backref='course')

        # Get course if it exists.
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

    print("\n%s courses added.\n\n" % (len(courses.keys())))

    print("Saving Students...")
    firebase_students = firebase_get("/schools/%s/students" % tng_id)
    for s in students:
        print(s)
        # print(s.__dict__)
        # get ID
        id = "1234"
        signup_date = 1234

        data = {
            "classes": {},
            "pictures": {
                "original": ""
            },
            "private": {
                "badge_count": 0,
                "email_buddy_request": "on",
                "email_groups": "everyone",
                "email_hearts": "buddies",
                "email_my_groups": "on",
                "email_private_message": "on",
                "push_buddy_request": "on",
                "push_groups": "everyone",
                "push_hearts": "everyone",
                "push_my_groups": "on",
                "push_private_message": "on"
            },
            "public": {
                "bio": s.bio,
                "buid": id,
                "first_name": s.full_name.split(" ")[0],
                "last_name": " ".join(s.full_name.split(" ")[1:]),
                "profile_pic_url_medium": "",
                "profile_pic_url_tiny": "",
                "signed_up_at": signup_date
            },
            "schools": {
                "%s" % tng_id: {
                    "id": "%s" % tng_id,
                    "name": SCHOOL_NAME[tng_id]
                }
            }

        }
        # print(data)
        for course in s.courses:
            if "%s" % course.id not in CLASSES_BY_PK:
                print("Missing %s" % course) 
            else:
                c_data = CLASSES_BY_PK["%s" % course.id]
                data["classes"][c_data["id"]] = c_data

        print(data)
        # Get/create accounts on server.
        # s.email_verified = 


        for buddy in s.buddies:
            print buddy
            # data["buddies"][""]



        # firebase_patch("schools/%s/classes/%s/" % (tng_id, id), {
        #     "code": data["profile"]["code"],
        #     "id": id,
        #     "name": get_class_name(c["subject"], c["code"]),
        #     "school_id": tng_id,
        #     "subject_code": data["profile"]["subject_code"],
        #     "subject_icon": data["profile"]["subject_icon"],
        #     "subject_name": data["profile"]["subject_name"],
        # })


        # firebase_put("schools/%s/students/%s/" % (tng_id, id), {
        #     ".value": True,
        #     "subject_name": data["profile"]["subject_name"],
        # })

        
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
    #     
    print(" - %s students" % (len(students)))
    print("Saving School...")
    
    # {
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
