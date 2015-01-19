#!/usr/bin/env python
import csv
import os
import sys
import argparse

sys.path.insert(0, os.getcwd())
from buddyup.database import Course, db, Language, Major


parser = argparse.ArgumentParser(description="Load a school's course, language, and major data")
parser.add_argument('school_name', metavar='N', type=str, nargs='+',
                   help='the school name (single word, data prefix)')


MIN_ENROLLMENT = 40
LANGUAGES = [
    "English",
    "American Sign Language",
    "Arabic",
    "Chinese - Cantonese",
    "Chinese - Mandarin",
    "Danish",
    "French",
    "German",
    "Greek",
    "Hebrew",
    "Hindi",
    "Italian",
    "Japanese",
    "Korean",
    "Latin",
    "Nepalese",
    "Norwegian",
    "Persian",
    "Polish",
    "Portugese",
    "Russian",
    "Spanish",
    "Swahili",
    "Swedish",
    "Telugu",
    "Turkish",
    "Vietnamese",
]
MAJORS = [
    "Accounting",
    "Aging Services",
    "Anthropology",
    "Applied Linguistics",
    "Architecture",
    "Art",
    "International Studies",
    "Biology",
    "Black Studies",
    "Business",
    "Chemistry",
    "Chicano/Latino Studies",
    "Child and Family Studies",
    "Civil Engineering",
    "Civic Leadership",
    "Communication",
    "Community Development",
    "Community Health",
    "International Studies - East Asia",
    "Biochemistry",
    "Computer Science",
    "Conflict Resolution",
    "Not Listed",
    "Criminology and Criminal Justice",
    "Dance",
    "Earth Science",
    "Economics",
    "Education",
    "Electric Engineering",
    "Electrical and Computer Engineering",
    "Engineering & Technology Management",
    "English: Writing",
    "Environmental Engineering",
    "Environmental Management",
    "Environmental Science and Management",
    "Environmental Studies",
    "European Studies",
    "Film",
    "Geography",
    "Geology",
    "Gerontology",
    "Health Care Management",
    "Health Studies",
    "History",
    "Indigenous Nations Studies",
    "Interdisciplinary Studies",
    "International Business Studies",
    "International Management",
    "Judaic Studies",
    "Latin American Studies",
    "Liberal Studies",
    "Mathematics",
    "Mathematics Educationn",
    "Mechanical Engineering",
    "Middle East Studies",
    "Music",
    "Nonprofit and Public Management",
    "Philosophy",
    "Physics",
    "Political Science",
    "Psychology",
    "Public Administration",
    "Public Affairs and Policy",
    "Science",
    "Service Learning",
    "Social Science",
    "Social Work",
    "Sociology",
    "Software Engineering",
    "Speech and Hearing Sciences",
    "Statistics",
    "Sustainability",
    "Systems Engineering",
    "Systems Science",
    "Technological Entrepreneurship",
    "Technology Management",
    "Theater Arts",
    "Transportation",
    "Urban Design",
    "Urban Studies and Planning",
    "Women's Studies",
    "World Languages",
    "Writing",
    "Graphic Design",
]

def main():
    args = parser.parse_args()
    with open(os.path.join(os.getcwd(), 'data/%s.csv' % (args.school_name[0])), 'rb') as csvfile:
        reader = csv.reader(csvfile)
        courses = {}
        for row in reader:
            name = u"%s" %row[1]
            num = int(row[0])
            if name in courses:
                courses[name]["num_students"] += num
            elif name != "":
                courses[name] = {"num_students": num}

    print "Adding courses.."
    for course_name, data in courses.iteritems():
        if data["num_students"] > MIN_ENROLLMENT:
            print "  %s (%s students):" % (course_name, data["num_students"]),
            matches = Course.query.filter(Course.name==course_name)
            if matches.count() > 0:
                print "exists."
            else:
                c = Course(name=course_name)
                db.session.add(c)
                print "added."

    print "Adding languages.."
    for language in LANGUAGES:
        print "  %s" % language,
        matches = Language.query.filter(Language.name==language)
        if matches.count() > 0:
            print "exists."
        else:
            l = Language(name=language)
            db.session.add(l)
            print "added."

    print "Adding majors.."
    for major in MAJORS:
        print "  %s" % major,
        matches = Major.query.filter(Major.name==major)
        if matches.count() > 0:
            print "exists."
        else:
            m = Major(name=major)
            db.session.add(m)
            print "added."

    db.session.commit()

if __name__ == '__main__':
    main()