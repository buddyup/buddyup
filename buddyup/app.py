import os, logging

from flask import Flask, g, session
from flask.ext.runner import Runner
from flask.ext.heroku import Heroku



app = Flask(__name__)
config_type = os.getenv('BUDDYUP_TYPE', 'dev').capitalize()
config_object = "{name}.config.{type}".format(name=__name__.split('.')[0],
                                              type=config_type)
app.config.from_object(config_object)
# NO_CDN: Default to using Content Distribution Network for libraries
# where possible.
app.config['USE_CDN'] = 'NO_CDN' not in os.environ

Heroku(app)

runner = Runner(app)


# In production mode, add log handler to sys.stderr.
if not app.debug:
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)


from . import database
from .templating import render_template
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
