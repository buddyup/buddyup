import os, logging

from flask import Flask, g, session
from flask.ext.runner import Runner
from flask.ext.heroku import Heroku



app = Flask(__name__)
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
from .util import login_required


@app.before_request
def setup():
    if 'user_id' in session:
        g.user = database.User.query.get(session['user_id'])
        # Invalid user id, kill the session with fire!
        if g.user is None:
            app.logger.warning("Session with uid %i is invalid, clearing session", session['user_id'])
            session.clear()
    else:
        g.user = None


@app.teardown_request
def teardown(*args):
    if hasattr(g, 'user'):
        del g.user


# Import after creating `app` to let pages.* have access to buddyup.app.app
from . import pages

# Insert others here...
