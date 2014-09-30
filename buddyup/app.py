import datetime
import os, logging

from flask import Flask, g, session, url_for, redirect, request
from flask.ext.runner import Runner
from flask.ext.heroku import Heroku
import mandrill


ALLOWED_UNVERIFIED_ENDPOINTS = ['verify_email', 'send_verify_email']
USER_VERIFY_EMAIL_GRACE_PERIOD = datetime.timedelta(hours=24)


app = Flask(__name__)
mandrill_client = mandrill.Mandrill('mZJ6dAVvZLkZ4faSdZRpvg')
config_type = os.getenv('BUDDYUP_TYPE', 'dev').capitalize()
config_object = "{name}.config.{type}".format(name=__name__.split('.')[0],
                                              type=config_type)
app.config.from_object(config_object)
# NO_CDN: Set the CDN environmental variable to use local files instead of
# CDN files.
app.config['USE_CDN'] = 'NO_CDN' not in os.environ

def from_env(*variables):
    for variable in variables:
        if variable in os.environ:
            app.config[variable] = os.environ[variable]

from_env('ADMIN_USER',
         'SECRET_KEY',
         'HELP_URL',
         'AWS_S3_BUCKET',
         'DEMO_MODE'
         )

if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

Heroku(app)

runner = Runner(app)


# In production mode, add log handler to sys.stderr.
if not app.debug:
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)


from . import database
from . import photo


def in_production():
    return config_type == "production"

@app.before_request
def setup():
    if 'user_id' in session:
        g.user = database.User.query.get(session['user_id'])
        # Invalid user id, kill the session with fire!
        if g.user is None:
            app.logger.warning("Session with uid %s is invalid, clearing session", session['user_id'])
            session.clear()
        else:
            # Verify 
            print request.endpoint
            print request.endpoint not in ALLOWED_UNVERIFIED_ENDPOINTS
            if "static/" not in request.path and\
                not g.user.email_verified and\
                g.user.created_at + USER_VERIFY_EMAIL_GRACE_PERIOD < datetime.datetime.now() and\
                request.endpoint not in ALLOWED_UNVERIFIED_ENDPOINTS:
                    print "redirect to the verify page"
                    return redirect("%s?next=%s" % (url_for('verify_email'), request.path))
    else:
        g.user = None


@app.teardown_request
def teardown(*args):
    if hasattr(g, 'user'):
        del g.user


# Import after creating `app` to let pages.* have access to buddyup.app.app
from . import pages

# Insert others here...

# TURN ON BELOW TO SEE QUERIES IN THE CONSOLE OR LOGS
# import logging
#
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)