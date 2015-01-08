#!/bin/sh
heroku run alembic upgrade head --app hudson-buddyup
heroku run alembic upgrade head --app buddyup
heroku run alembic upgrade head --app oregonstate-buddyup
heroku run alembic upgrade head --app ecampus-oregonstate-buddyup
heroku run alembic upgrade head --app buddyup
heroku run alembic upgrade head --app buddyup-skylinecollege
heroku run alembic upgrade head --app buddyup-canadacollege
heroku run alembic upgrade head --app buddyup-collegeofsanmateo
heroku run alembic upgrade head --app buddyup-ohsu