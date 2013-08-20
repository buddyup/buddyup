from flask import g

from buddyup.app import app
from buddyup.database import (User, Buddy, BuddyInvitation,
                              db)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get
from buddyup.database import User

@app.route("/buddy/view/<user_name>")
@login_required
def buddy_view(user_name):
    buddy_record = User.query.filter_by(user_name=user_name).first_or_404()
    return render_template('buddy/view.html', buddy_record=buddy_record)


@app.route("/buddy/search")
@login_required
def buddy_search():
    # TODO: implement this stuff!
    #buddies = g.user.buddies.all()
    return render_template('buddy/buddies.html',
                           buddies=buddies)


@app.route("/buddy/search_result")
@login_required
def buddy_search_results():
    name = args_get('name')
    language = args_get('language', convert=int)
    course = args_get('course', convert=int)
    query = Buddy.query
    if name:
        query = query.filter(User.full_name.like('%' + name + "%"))
    query = query.filter(Buddy.language_id == language)
    query = query.filter(Buddy.user2.course_id == course)
    buddies = query.all()
    return render_template('buddy/search_results.html', buddies=buddies)
