from flask import url_for, redirect, g

from buddyup.app import app
from buddyup.database import User
from buddyup.templating import render_template
from buddyup.util import login_required, events_to_json

# Expect behavior: '/' redirects to 


@app.route('/')
def index():
    if g.user is None:
        # Note that this landing/intro "/" page is only used for testing/development.  
        # For the production site, the landing/intro "/" page is hosted on weebly.
        all_users = User.query.all()
        all_usernames = sorted([str(user.user_name) for user in all_users])
        return render_template('intro.html', all_usernames=all_usernames, cas_service=app.cas_service)
    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    # select events for all classes we are in
    users = User.query.all()
    for user in users:
        if user.has_photos == True:
            continue
        else:
            users.remove(user)
    return render_template('index.html', users = users)


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