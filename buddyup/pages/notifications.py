from flask import g, request, abort, redirect, url_for

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership,
                              Course, CourseMembership, db,
                              Location, Action)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages, shuffled, track_activity

from collections import defaultdict


@app.route("/notifications")
@login_required
@track_activity
def list_notifications():
    return render_template('notifications/list.html', notifications=g.user.notifications, user=g.user)


