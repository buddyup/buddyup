#!/usr/bin/env python

import csv
import os
import sys
import argparse

sys.path.insert(0, os.getcwd())
from buddyup.database import Course, db


parser = argparse.ArgumentParser(description="Load a school's course, language, and major data")
parser.add_argument('school_name', metavar='N', type=str, nargs='+',
                   help='the school name (single word, data prefix)')

parser.add_argument('--skip-courses', dest='skip_courses', action='store_const',
                   const=True, default=False,
                   help='Skip course import')

MIN_ENROLLMENT = 40

def main():
    args = parser.parse_args()
    if not args.skip_courses:
        with open(os.path.join(os.getcwd(), 'data/old_bad_data/%s.csv' % (args.school_name[0])), 'rb') as csvfile:
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
                    for m in matches:
                        if m.users.count() > 0:
                            print "has followers."
                        else:
                            print "empty"
                            Course.query.filter_by(id=m.id).delete()
                else:
                    print "not found"

    db.session.commit()

if __name__ == '__main__':
    main()