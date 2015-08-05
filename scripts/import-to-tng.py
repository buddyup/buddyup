#!/usr/bin/env python
import csv
import os
import json
import hashlib
import requests
import re
import sys
import time

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
from buddyup.photo import get_photo_url

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
FIREBASE_KEY = os.environ["FIREBASE_KEY"]
API_ENDPOINT = os.environ["API_ENDPOINT"]


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


def find_photo(user):
    # I know. This is insane. But they never stored a backref on photo.
    print(user.user_name)
    print(Photo)
    print(Photo.query)
    for p in Photo.query:
        print(p.url)
        if user.user_name in p.url and p.x != 50 and p.x != 200:
            print("found photo!")
            return p


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
    print("\n%s courses added.\n\n" % (len(courses.keys())))

    print("Saving Students...")
    firebase_students = firebase_get("/schools/%s/students" % tng_id)
    for s in students:
        # print(data)
        if tng_id == "buddyup_org" or tng_id == "pdx_edu" and not s.email:
            s.email = "%s@pdx.edu" % s.user_name

        # Get/create accounts on server.
        account_data = {
            "email": s.email,
            "secret": FIREBASE_KEY,
            "created_at": int(time.mktime(s.created_at.timetuple()) * 1000),
            "email_verified": s.email_verified,
        }

        json_header = {'content-type': 'application/json'}
        r = requests.post(
            "%sv1/internal/migrate-user" % API_ENDPOINT,
            data=json.dumps(account_data),
            headers=json_header
        )
        assert r.status_code == 200
        resp = r.json()
        assert r.json()["success"] is True
        id = r.json()["buid"]

        signup_date = r.json()["created_at"]

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
        # Classes
        for course in s.courses:
            if "%s" % course.id not in CLASSES_BY_PK:
                # print("Missing %s" % course)
                pass
            else:
                c_data = CLASSES_BY_PK["%s" % course.id]
                data["classes"][c_data["id"]] = c_data

        student_data[s.email] = data

    # Loop again now that we have full data.
    print("\nDoing actual adds.")
    for s in students:
        if tng_id == "buddyup_org" or tng_id == "pdx_edu" and not s.email:
            s.email = "%s@pdx.edu" % s.user_name

        data = student_data[s.email]
        buid = data["public"]["buid"]

        if buid not in firebase_students:

            # Buddies
            for buddy in s.buddies:
                if tng_id == "buddyup_org" or tng_id == "pdx_edu" and not buddy.email:
                    buddy_email = "%s@pdx.edu" % buddy.user_name
                else:
                    buddy_email = buddy.email

                if not "buddies" in data:
                    data["buddies"] = {}

                buddy_buid = student_data[buddy_email]["public"]["buid"]

                if buddy_buid not in data["buddies"]:
                    data["buddies"][buddy_buid] = {}

                data["buddies"][buddy_buid]["first_name"] = student_data[buddy_email]["public"]["first_name"]
                data["buddies"][buddy_buid]["last_name"] = student_data[buddy_email]["public"]["last_name"]
                data["buddies"][buddy_buid]["user_id"] = student_data[buddy_email]["public"]["buid"]

            # Picture
            picture = find_photo(s)
            assert picture is not None
            url = get_photo_url(s, picture)
            print ("found photo: %s" % url)

            image = requests.get(url)

            data["pictures"] = {
                "original": "data:image/png;base64,%s" % image.content
            }
            data["public"]["profile_pic_url_medium"] = ""
            data["public"]["profile_pic_url_tiny"] = ""

            print(data)
            firebase_patch("users/%s/" % buid, data)
            raise Exception

            # Kick off thumbnails
            account_data = {
                "buid": buid,
                "secret": FIREBASE_KEY,
            }

            json_header = {'content-type': 'application/json'}
            r = requests.post(
                "%sv1/internal/migrate-picture" % API_ENDPOINT,
                data=json.dumps(account_data),
                headers=json_header
            )
            assert r.status_code == 200

            # Add to class classmates
            for class_id, class_data in data["classes"].items():
                firebase_put("classes/%s/students/%s/" % (class_id, buid), {
                    ".value": True,
                    "subject_name": data["profile"]["subject_name"],
                })

            # Add to School's students
            firebase_put("schools/%s/students/%s/" % (tng_id, buid), {
                ".value": True,
            })

    print(" - %s students" % (len(students)))


def main():
    import_data()    

if __name__ == '__main__':
    main()
