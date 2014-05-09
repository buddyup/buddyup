import random

from flask import url_for, redirect, g

from buddyup.app import app
from buddyup.database import User
from buddyup.templating import render_template
from buddyup.util import login_required, events_to_json, shuffled


HOME_LIMIT = 30

# Expect behavior: '/' redirects to 

@app.route('/')
def index():
    if g.user is None:
        try:
            # Note that this landing/intro "/" page is only used for testing/development.
            # For the production site, the landing/intro "/" page is hosted on weebly.
            ENABLE_AUTHENTICATION = app.config['BUDDYUP_ENABLE_AUTHENTICATION']
            all_users = User.query.order_by(User.user_name).all()
            all_usernames = [user.user_name for user in all_users]
            raise "WHATEVER"
            return render_template('intro.html',
                                   ENABLE_AUTHENTICATION=ENABLE_AUTHENTICATION,
                                   all_usernames=all_usernames,
                                   cas_service=app.cas_service)
        except:
            # An error that catastrophic should only happen with a brand new instance.
            return render_template('new_instance.html')

    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    # TODO: Possible scaling issue. Loads, shuffles, and listifies all classmates in memory? Can the DB handle this for us?
    # Calculate fellow students without duplicates.
    # SQLAlchemy ORM objects are unique to the session, not to an
    # individual query, so we can use a set.
    unordered_classmates = set()
    for course in g.user.courses.all():
        for other in course.users.filter(User.has_photos == True,
                                         User.id != g.user.id).all():
            unordered_classmates.add(other)

    classmates = shuffled(unordered_classmates)
    count = len(classmates)
    del classmates[HOME_LIMIT:]

    return render_template('index.html',
                           classmates=classmates,
                           count=count) 


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