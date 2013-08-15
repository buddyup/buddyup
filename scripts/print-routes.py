#!/usr/bin/env python
import sys, os

sys.path.insert(0, os.getcwd())

from buddyup import app
for rule in app.url_map.iter_rules():
    print rule.endpoint, '->', rule