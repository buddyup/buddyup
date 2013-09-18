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
if 'ADMIN_USER' in os.environ:
    app.config['ADMIN_USER'] = os.environ['ADMIN_USER']
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
if 'HELP_URL' in os.environ:
    app.config['HELP_URL'] = os.environ['HELP_URL']
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
            app.logger.warning("Session with uid %i is invalid, clearing session")
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
