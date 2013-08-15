#!/usr/bin/env python
import sys, os

sys.path.insert(0, os.getcwd())

from buddyup import app
rules = sorted(app.url_map.iter_rules(), key=lambda rule: rule.endpoint)

for rule in rules:
    print rule.endpoint, '->', rule