from flask import url_for, redirect, g

from buddyup.app import app
from buddyup.templating import render_template
from buddyup.util import login_required, events_to_json

# Expect behavior: '/' redirects to 


@app.route('/')
def index():
    if g.user is None:
        return render_template('intro.html')
    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    # select events for all classes we are in
    events = []
    for course in g.user.courses.all():
        events.extend(course.events)
    event_json = events_to_json(events)
    return render_template('index.html', events_json=event_json)


@app.route('/help')
@login_required
def help():
    help_url = app.config.get('HELP_URL')
    if help_url is None:
        return render_template('help.html')
    else:
        return redirect(help_url)


@app.route('/suggestions')
@login_required
def suggestions():
    return render_template('setup/suggestions.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('setup/welcome.html')