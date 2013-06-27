from flask import Flask, g, request

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BUDDYUP_SETTINGS', silent=True)

import database

@app.before_request
def setup():
    if 'uid' in request.session:
        user = database.User.query.get(user_id)
        # Invalid user id, kill the session with fire!
        if user is None:
            app.logger.warning("Session with uid %i is invalid, clearing session")
            request.session.clear()
    else:
        g.user = None


@app.teardown_request
def teardown():
    del g.user

# Import after creating `app` to let pages.* have access to buddyup.app.app
import pages

# Insert others here...