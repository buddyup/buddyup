from buddyup.database import db, Location, Language, Major, Course, User

import sys
from os import environ

if environ.get("DEMO_SITE", "") != "true":
    print "You can only load demo data on a demo server instance. Aborting."
    sys.exit()


import sys, os
sys.path.insert(0, os.getcwd())

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
db.session.add(Language(name="Spanish"))
db.session.add(Language(name="Cantonese"))
db.session.add(Language(name="Mandarin"))
db.session.add(Language(name="Hindi"))
db.session.add(Language(name="French"))


print "Creating majors"
# Major
db.session.add(Major(name="Architecture"))
db.session.add(Major(name="Business"))
db.session.add(Major(name="Psychology"))
db.session.add(Major(name="Mathematics"))
db.session.add(Major(name="Physics"))


print "Creating courses"
# Courses
db.session.add(Course(name="MATH 340", instructor="Hudson University")) # Calculus for Business and Economics
db.session.add(Course(name="STAT 300", instructor="Hudson University")) # Introduction to Probability and Statistics
db.session.add(Course(name="BIOL 102", instructor="Hudson University")) # Essentials of Human Anatomy and Physiology
db.session.add(Course(name="ART 324", instructor="Hudson University")) # Collage and Assemblage
db.session.add(Course(name="HIST 365", instructor="Hudson University")) # Asian Civilization


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
    user.bio = """Taking a full load this term and looking to stay on top of things. 
    If you want to make a study group for any of my classes, send me a buddy invite.
    I'm usually on campus weekdays between 10 and 4."
    """
    user.location=lookup_location("On-campus")
    user.courses=[lookup_course("MATH 340")]
    user.majors=[lookup_major("Architecture")]
    user.languages=[lookup_language("Spanish")]

    return user


user_info = [
    ("Ted Mosby", "Architecture"),
    ("Barney Stinson", "Business"),
    ("Camilla Washington", "Psychology"),
    ("Lynn Nguyen", "Mathematics"),
    ("Jack King", "Physics"),
]


users = [create_user(u) for u in user_info]

print "Creating users"

for user in users:
    print "Adding {}".format(user.full_name)
    db.session.add(user)

db.session.commit()
