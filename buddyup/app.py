from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BUDDYUP_SETTINGS', silent=True)

# Import after creating `app` to let pages.* have access to buddyup.app.app
import pages

# Insert others here...