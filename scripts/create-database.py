#!/usr/bin/env python
import sys, os

sys.path.insert(0, os.getcwd())

import buddyup.database
buddyup.database.db.create_all()