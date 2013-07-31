import os

from flask import Flask, g, session
from flask.ext.runner import Runner
from flask.ext.heroku import Heroku



app = Flask(__name__)
config_type = os.getenv('BUDDYUP_TYPE').capitalize()
config_object = "{name}.config.{type}".format(name=__name__.split('.')[0],
                                              type=config_type)
app.config.from_object(config_object)
app.config.from_envvar('BUDDYUP_SETTINGS', silent=True)

runner = Runner(app)

from . import database
from . import templating

@app.before_request
def setup():
    if 'uid' in session:
        user = database.User.query.get('user_id')
        # Invalid user id, kill the session with fire!
        if user is None:
            app.logger.warning("Session with uid %i is invalid, clearing session")
            session.clear()
    else:
        g.user = None


@app.teardown_request
def teardown(*args):
    if hasattr(g, 'user'):
        del g.user


@app.route('/')
def index():
    return templating.render_template('index.html')


# Import after creating `app` to let pages.* have access to buddyup.app.app
from . import pages

# Insert others here...
