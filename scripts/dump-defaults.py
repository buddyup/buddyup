#!/usr/bin/env python
import sys, os, argparse, io, logging, logging.handlers, csv

logger = logging.getLogger('populate')

sys.path.insert(0, os.getcwd())

from buddyup.database import db, Location, Major, Language, Course

parser = argparse.ArgumentParser(
    description="Dump defaults from the database")
parser.add_argument('--list-targets', '-l', action="store_true",
                    help="List dump targets")
parser.add_argument('--out', '-o', default="-",
                    help="Output file, - for stdout")
parser.add_argument('target', nargs="?")

dumpers = {}


def dumper(f):
    dumpers[f.__name__] = f
    return f


def field_dumper(model, field):
    for record in model.query.all():
        yield getattr(record, field)


@dumper
def location():
    for i in field_dumper(Location, "name"):
        yield i,


@dumper
def language():
    for i in field_dumper(Language, "name"):
        yield i,


@dumper
def major():
    for i in field_dumper(Major, "name"):
        yield i,


@dumper
def course():
    for record in Course.query.all():
        yield record.name, record.instructor


def main():
    args = parser.parse_args()
    if args.list_targets:
        for name in sorted(dumpers.keys()):
            print name
        exit(0)
    dumper = dumpers.get(args.target)
    if dumper is None:
        print "Invalid dumper '%s'" % args.target
        exit(1)
    if args.out == '-':
        f = sys.stdout
    else:
        f = io.open(args.out, 'rb')
    writer = csv.writer(f)
    try:
        for item in sorted(dumper()):
            encoded = [s.encode('utf8') for s in item]
            writer.writerow(encoded)
            
    finally:
        f.close()

 
if __name__ == "__main__":
    main()