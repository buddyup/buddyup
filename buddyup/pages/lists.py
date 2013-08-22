from flask import g

from buddyup.app import app
from buddyup.templating import render_template


@app.route("/my/groups_and_events")
def buddy_group_list():
    buddies = g.user.buddies.all()
    groups = g.user.events.all()
    return render_template('my/buddies_and_groups.html',
                           buddies=buddies,
                           groups=groups,
                           )
