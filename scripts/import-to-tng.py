#!/usr/bin/env python
import base64
import boto
import csv
from collections import namedtuple
import os
import json
import hashlib
from io import BytesIO
import requests
import re
import sys
import time
from PIL import Image, ImageOps, ExifTags

Dimensions = namedtuple('Dimensions', 'x y')


ORIGINAL_SIZE = Dimensions(1200, 1200)

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
    "BIOL": {"icon": "paw", "name": "Biology", },
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
    "HIST": {"icon": "university", "name": "History", },
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
    # OIT
    "ACAD": {"icon": "lightbulb-o", "name": "Academic Success", },
    "ACC": {"icon": "calculator", "name": "Accounting", },
    "CHE": {"icon": "flask", "name": "Chemistry", },
    "DMS": {"icon": "medkit", "name": "Diagnostic Medical Sonography", },
    "ECO": {"icon": "university", "name": "Economics", },
    "EE": {"icon": "calculator", "name": "Electrical Engineering", },
    "MGT": {"icon": "building", "name": "Management", },
    "MIS": {"icon": "building", "name": "Management Information Systems", },
    "MIT": {"icon": "medkit", "name": "Medical Imaging Technology", },
    "Other": {"icon": "cutlery", "name": "Other", },
    "PHY": {"icon": "globe", "name": "Physics", },
    "REE": {"icon": "lightbulb-o", "name": "Renewable Energy Engineering", },
    "SPE": {"icon": "globe", "name": "Speech", },
    "WRI": {"icon": "pencil", "name": "Writing", },
    # OSU E-Campus
    "FW": {"icon": "paw", "name": "Fisheries and Wildlife", },
    "HDFS": {"icon": "globe", "name": "Human Dev and Family Sciences", },
    "ENGR": {"icon": "calculator", "name": "Engineering Sciences", },
    "MB": {"icon": "flask", "name": "Microbiology", },
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

SCHOOL_NAME = {
    "pdx_edu": "Portland State University",
    "buddyup_org": "BuddyUp University",
    "oregonstate_edu": "Oregon State University",
    "oit_edu": "Oregon Institute of Technology",
    "oregonstate_edu": "Oregon State University",
    "smccd_edu": "San Mateo Community College District",
    "stanford_edu": "Stanford",
    "sydney_edu_au": "University of Sydney",
    "hudson_edu": "Hudson University",
}



IGNORE_SUBJECT_LIST = [
    "OTHER",
    "Group Theory",
    "421-526",
]

tng_id = os.environ["TNG_ID"]
FIREBASE_KEY = os.environ["FIREBASE_KEY"]
API_ENDPOINT = os.environ["API_ENDPOINT"]
bucket_name = os.environ["AWS_S3_BUCKET"]

CLASS_NAME_MAPPING = {}
PHOTO_LIST = []


class Blank():
    pass

if tng_id == "buddyup_org":
    bucket_name = 'buddyuppdx'

conn = boto.connect_s3()
try:
    bucket = conn.get_bucket(bucket_name)
    for key in bucket.list():
        PHOTO_LIST.append(key.name.encode('utf-8'))
except:
    import traceback; traceback.print_exc();

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
    potentials = []
    for p in PHOTO_LIST:
        if user.user_name in p:
            x = int(p.split(".")[0].split("-")[-2])
            y = int(p.split(".")[0].split("-")[-1])
            potentials.append({
                "x": x,
                "y": y,
                "url": p
            })
    biggest = 0
    biggest_url = None
    size = Blank()
    for p in potentials:
        if p["x"] > biggest:
            biggest = p["x"]
            biggest_url = p["url"]
            size.x = p["x"]
            size.y = p["y"]
    if biggest_url:
        print("found photo (%s)!" % biggest)
    else:
        print("no photo found for %s" % user)
    return biggest_url, size


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
        print(r.content)
        print(r.text)
        print(r.json())
    try:
        assert r.status_code == 200
    except:
        print(r.status_code)
        # print(data)
        raise


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
                # print "Error parsing %" % name

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
        if not firebase_subjects or s["code"] not in firebase_subjects:
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

    missing_photos = []

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
            "school_code": tng_id,
            "first_name": s.full_name.split(" ")[0],
            "last_name": " ".join(s.full_name.split(" ")[1:]),
        }

        json_header = {'content-type': 'application/json'}
        r = requests.post(
            "%sv1/internal/migrate-user" % API_ENDPOINT,
            data=json.dumps(account_data),
            headers=json_header
        )
        if not r.status_code == 200:
            print "Failed to migrate user"
            print account_data
        else:
            resp = r.json()
            assert r.json()["success"] is True
            buid = r.json()["buid"]
            if r.json()["buid"] is None:
                print(account_data)
                raise Exception("No buid for %s" % r.json())

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
                    "push_private_message": "on",
                    "migrated": True,
                    "has_completed_migration": False,
                },
                "internal": {
                    "email_verified": True,
                },
                "public": {
                    "bio": s.bio,
                    "buid": r.json()["buid"],
                    "first_name": s.full_name.split(" ")[0],
                    "last_name": " ".join(s.full_name.split(" ")[1:]),
                    "profile_pic_url_medium": "",
                    "profile_pic_url_tiny": "",
                    "signed_up_at": signup_date,
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

    print("Missing photos for %s students" % len(missing_photos))
    print(missing_photos)

    # Loop again now that we have full data.
    print("\nDoing actual adds.")
    for s in students:
        if tng_id == "buddyup_org" or tng_id == "pdx_edu" and not s.email:
            s.email = "%s@pdx.edu" % s.user_name

        if s.email in student_data: 
            data = student_data[s.email]
            buid = data["public"]["buid"]
            print(data["public"])

            if not firebase_students or buid not in firebase_students:

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

                # # Picture
                picture, size = find_photo(s)
                if picture:
                    url = "http://%s.s3.amazonaws.com/%s" % (
                        bucket_name,
                        picture,
                    )
                else:
                    url = "https://s3-us-west-2.amazonaws.com/buddyup-core/add_photo_high_res.png"

                data["public"]["profile_pic_url_medium"] = ""
                data["public"]["profile_pic_url_tiny"] = ""

                print("patching user data")
                for k, v in data.items():
                    print(k)
                    firebase_patch("users/%s/%s" % (buid, k), v)

                print ("found photo: %s" % url)
                image = requests.get(url)
                print len(image.content)
                base_image = Image.open(BytesIO(image.content))

                try:
                    for orientation in ExifTags.TAGS.keys() : 
                        if ExifTags.TAGS[orientation]=='Orientation' : break 
                    exif=dict(base_image._getexif().items())
                    if orientation in exif:
                        if   exif[orientation] == 3 : 
                            base_image=base_image.rotate(180, expand=True)
                        elif exif[orientation] == 6 : 
                            base_image=base_image.rotate(270, expand=True)
                        elif exif[orientation] == 8 : 
                            base_image=base_image.rotate(90, expand=True)
                except AttributeError, KeyError:
                    # import traceback; traceback.print_exc();
                    pass

                resized = ImageOps.fit(base_image, ORIGINAL_SIZE, method=Image.ANTIALIAS, centering=(0.5, 0.5))
                print "resized."
                print len(resized.tobytes())
                output = BytesIO()
                resized.save(output, format="PNG")
                print("patching profile pic")
                firebase_patch("users/%s/pictures" % buid, {
                    "original": "data:image/png;base64,%s" % base64.b64encode(output.getvalue())
                })

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
                    })

                # Add to School's students
                firebase_put("schools/%s/students/%s/" % (tng_id, buid), {
                    ".value": True,
                })

    print(" - %s students" % (len(students)))
    print("Missing photos for %s" % len(missing_photos))

def main():
    import_data()

if __name__ == '__main__':
    main()
