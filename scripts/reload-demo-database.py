import random
import os
import sys
from os import environ

if environ.get("DEMO_SITE", "").lower() != "true":
    print "You can only load demo data on a demo server instance. Aborting."
    sys.exit()


sys.path.insert(0, os.getcwd())


from buddyup.database import db, Location, Language, Major, Course, User, Tutor

COURSES = [
    "MATH 340", # Calculus for Business and Economics
    "STAT 300", # Introduction to Probability and Statistics
    "BIOL 102", # Essentials of Human Anatomy and Physiology
    "ART 324", # Collage and Assemblage
    "HIST 365", # Asian Civilization
]
MAJORS = [
    "Architecture",
    "Business",
    "Psychology",
    "Mathematics",
    "Physics",
]
LANGUAGES = [
    "English",
    "Spanish",
    "Cantonese",
    "Mandarin",
    "Hindi",
    "French",
]


print "Dropping database"
db.drop_all()

print "Creating database"
db.create_all()


"""
Create demo data to support demo/sales purposes.
"""

print "Creating locations"
# Locations
db.session.add(Location(name="On-campus"))
db.session.add(Location(name="North of campus"))
db.session.add(Location(name="West of campus"))
db.session.add(Location(name="East of campus"))
db.session.add(Location(name="South of campus"))


print "Creating languages"
# Languages
for l in LANGUAGES:
    db.session.add(Language(name=l))

print "Creating majors"
# Major
for m in MAJORS:
    db.session.add(Major(name=m))

print "Creating courses"
# Courses
for c in COURSES:
    db.session.add(Course(name=c, instructor="Hudson University"))

# Save all of these so we can compose users from them.
db.session.commit()


# Users

def user_name(full_name):
    return full_name.lower()[0] + full_name.split(' ')[-1].lower()

def lookup_course(name):
    return Course.query.filter(Course.name==name).first()

def lookup_language(name):
    return Language.query.filter(Language.name==name).first()

def lookup_location(name):
    return Location.query.filter(Location.name==name).first()

def lookup_major(name):
    return Major.query.filter(Major.name==name).first()

def create_user(user_info):
    full_name, major = user_info
    user = User()
    user.full_name=full_name
    user.user_name=user_name(full_name),
    user.bio = """Taking a full load this term and looking to stay on top of things. If you want to make a study group for any of my classes, send me a buddy invite. I'm usually on campus weekdays between 10 and 4."""
    user.location = lookup_location("On-campus")
    user.courses = [lookup_course(c) for c in random.sample(COURSES, 2)]
    user.majors = [lookup_major(random.choice(MAJORS))]
    user.languages = [lookup_language("English"), lookup_language(random.choice(LANGUAGES))]
    user.skype = user.user_name
    user.verified = True
    user.has_photos = True
    user.email_verified = True
    user.email = "info+%s@buddyup.org" % user_name(full_name)

    return user


user_info = [
    ("Dwayne Johnson","Architecture"),
    ("Bob Sakimoto","Business"),
    ("Flor Kwon","Psychology"),
    ("Javier Buchanan","Mathematics"),
    ("Lily Li","Physics"),
    ("James Smith","Architecture"),
    ("Caitlin Ramirez","Business"),
    ("Marcelo Gonzalez","Psychology"),
    ("Michelle Forbes","Mathematics"),
    ("Kim Green","Physics"),
    ("Kimberley Miller","Architecture"),
    ("JJ James","Business"),
    ("John Malloy","Psychology"),
    ("John Samberg","Mathematics"),
    ("Liz Martin","Physics"),
    ("Elizabeth Tran","Architecture"),
    ("Waseem Ahmed","Business"),
    ("Benjamin Cho","Psychology"),
    ("Maciej Matuszak","Mathematics"),
    ("Brie Stinson","Physics"),
    ("Shanice Labatt","Architecture"),
    ("Dylan Camus","Business"),
    ("Brett Fong","Psychology"),
    ("Stephanie Flores","Mathematics"),
    ("Leticia Ericsson","Physics"),
    ("Molly Grace","Architecture"),
    ("Martha Weir","Business"),
    ("Debbie Allen","Psychology"),
    ("Jacqueline Beauchamp","Mathematics"),
    ("Kris Summers","Physics"),
    ("Monica Macdonald","Architecture"),
]


users = [create_user(u) for u in user_info]

print "Creating users"

for user in users:
    print "Adding {} {}".format(user.full_name, user.email)
    db.session.add(user)
    db.session.commit()
    if random.choice([True,False]):
        print " - a tutor"
        t = Tutor()
        t.user_id = user.id
        t.approved = True
        t.courses.append(lookup_course(random.choice(COURSES)))
        db.session.add(t)
        db.session.commit()
