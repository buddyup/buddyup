#!/usr/bin/env python
import sys, os, argparse, io, logging, logging.handlers

logger = logging.getLogger('populate')

sys.path.insert(0, os.getcwd())

import buddyup.database
from buddyup.database import db, Location, Major


parser = argparse.ArgumentParser()
parser.add_argument('--clear', '-c', action="store_true",
                    help="Clear old records")
parser.add_argument('--verbose', '-v', action="store_true",
                    help="Print while you insert!")
parser.add_argument('targets', nargs='+')

populators = {}


def populate_location(args):
    if args.clear:
        Major.query.delete()
    for location in read_defaults('locations'):
        if Location.query.filter_by(name=location).count() < 1:
            logger.info("Inserting location '%s'", location)
            record = Location(name=location)
            db.session.add(record)
        else:
            logger.info("Skipping location '%s'", location)
    db.session.commit()


populators['location'] = populate_location


def populate_majors(args):
    if args.clear:
        Major.query.delete()
    for major in read_defaults('major'):
        if Major.query.filter_by(name=major).count() < 1:
            logger.info("Inserting major '%s'", major)
            record = Major(name=major)
            db.session.add(record)
        else:
            logger.info("Skipping major '%s'", major)
    db.session.commit()


populators['major'] = populate_majors


def read_defaults(target):
    with io.open(os.path.join('defaults', target + '.txt')) as f:
        for line in f:
            yield line.rstrip('\r\n')


def main():
    args = parser.parse_args()
    if args.verbose:
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)
    target_names = set(args.targets)
    if 'all' in target_names:
        targets = [target for name, target in sorted(populators.items())]
    else:
        targets = map(populators.get, sorted(target_names))
        if None in targets:
            print("Unknown target")
            exit(1)
    for target in targets:
        target(args)

if __name__ == '__main__':
    main()