import random

from flask import url_for, redirect, g

from buddyup.app import app
from buddyup.database import User
from buddyup.templating import render_template
from buddyup.util import login_required, events_to_json


HOME_ROW_WIDTH = 5
HOME_LIMIT = 15


# Expect behavior: '/' redirects to 

@app.route('/')
def index():
    if g.user is None:
        # Note that this landing/intro "/" page is only used for testing/development.  
        # For the production site, the landing/intro "/" page is hosted on weebly.
        ENABLE_AUTHENTICATION = app.config['BUDDYUP_ENABLE_AUTHENTICATION']
        all_users = User.query.order_by(User.user_name).all()
        all_usernames = [user.user_name for user in all_users]
        return render_template('intro.html',
                               ENABLE_AUTHENTICATION=ENABLE_AUTHENTICATION,
                               all_usernames=all_usernames,
                               cas_service=app.cas_service)
    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    # Calculate fellow students without duplicates
    users = {}
    for course in g.user.courses.all():
        for other in course.users.filter(User.has_photos == True,
                                         User.id != g.user.id).all():
            users[other.id] = other

    # Python 3: Change to list(users.values())
    filtered_users = users.values()
    random.shuffle(filtered_users)

    # Limit to HOME_LIMIT users
    del filtered_users[HOME_LIMIT:]

    rows = []
    for i in range(0, len(filtered_users), HOME_ROW_WIDTH):
        rows.append(filtered_users[i:i + HOME_ROW_WIDTH])
    return render_template('index.html', print_users=rows)


@app.route('/help')
@login_required
def help():
    return redirect('http://www.getbuddyup.com/faq.html')


@app.route('/suggestions')
@login_required
def suggestions():
    return render_template('setup/suggestions.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('setup/welcome.html')

@app.route('/term_and_conditions')
def term_conditions():
    return render_template('setup/term_conditions.html')