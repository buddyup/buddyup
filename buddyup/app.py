from flask import Flask, g, session
from flask.ext.runner import Runner



app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BUDDYUP_SETTINGS', silent=True)

import database
import templating

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


# Import after creating `app` to let pages.* have access to buddyup.app.app
import pages

# Insert others here...