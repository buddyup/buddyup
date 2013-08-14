from flask import g

from buddyup.app import app
from buddyup.database import User, db 
from buddyup.templating import render_template
from buddyup.util import login_required, args_get
from buddyup.database import User

@app.route("/buddy/view/<user_name>")
@login_required
def view_buddy(user_name):
    buddy_record = User.query.filter_by(user_name=user_name).first_or_404()
    return render_template('buddy/view.html', buddy_record=buddy_record)


@app.route("/buddy/search")
@login_required
def search_buddies():
    # TODO: implement this stuff!
    buddies = g.user.buddies.all()
    return render_template('buddy/search.html',
                           buddies=buddies)


@app.route("/buddy/search_result")
@login_required
def search_results_buddies():
    raise NotImplemented()
