from buddyup.database import db, Location, Language, Major, Course, User

import sys
from os import environ

if environ.get("DEMO_SITE", "") != "true":
    print "You can only load demo data on a demo server instance. Aborting."
    sys.exit()


"""
Create demo data to support demo/sales purposes.
"""

# Locations
db.session.add(Location(name="On-campus"))
db.session.add(Location(name="North of campus"))
db.session.add(Location(name="West of campus"))
db.session.add(Location(name="East of campus"))
db.session.add(Location(name="South of campus"))


# Languages
db.session.add(Language(name="Spanish"))
db.session.add(Language(name="Cantonese"))
db.session.add(Language(name="Mandarin"))
db.session.add(Language(name="Hindi"))
db.session.add(Language(name="French"))


# Major
db.session.add(Major(name="Architecture"))
db.session.add(Major(name="Business"))
db.session.add(Major(name="Psychology"))
db.session.add(Major(name="Mathematics"))
db.session.add(Major(name="Physics"))

# Courses

db.session.add(Course(name="MATH 340", instructor="Hudson University")) # Calculus for Business and Economics
db.session.add(Course(name="STAT 300", instructor="Hudson University")) # Introduction to Probability and Statistics
db.session.add(Course(name="BIOL 102", instructor="Hudson University")) # Essentials of Human Anatomy and Physiology
db.session.add(Course(name="ART 324", instructor="Hudson University")) # Collage and Assemblage
db.session.add(Course(name="HIST 365", instructor="Hudson University")) # Asian Civilization

# Save all of these so we can compose users from them.
db.session.commit()


# Users

users = []

users.append( create_user("Ted Mosby", "Architecture")
)


"Ted Mosby", 
"Barney Stinson", Business
"Camilla Washington", Psychology
"Lynn Nguyen", Mathematics
"Jack King", Physics

for user in users:
    user.initialized = True
    user.email_verified = True
    user.has_photos = True
    user.bio = "I'm trying to get better grades"
    user.email = "info+{.user_name}@buddyup.org".format(user)


User()



class User(db.Model):
    user_name
    full_name
    location
    courses
    majors
    languages

def user_name(full_name):
    return full_name.lower()[0] + full_name.split(' ')[-1].lower()

def create_user(full_name, major):
    user = User()
    user.full_name="Ted Mosby",
    user.user_name=user_name(full_name),
    user.location
    user.courses
    user.majors=[LookupMajor("Architecture")]
    user.languages










