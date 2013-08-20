from flask import (g, abort, get_flashed_messages, request, flash, redirect,
                   url_for)

from sqlalchemy.sql import functions

from buddyup.app import app
from buddyup.database import Course, Visit, Event, User, BuddyInvitation, db
from buddyup.templating import render_template
from buddyup.util import form_get, check_empty
from functools import partial, wraps


def admin_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if g.user and g.user.user_name == app.config.get("ADMIN_USER", u""):
            return f(*args, **kwargs)
        else:
            abort(403)
    return func


def get_stats():
    variables = {}
    variables['group_count'] = Event.query.count()
    variables['unique_visits'] = Visit.query.count()
    query = db.session.query(functions.sum(Visit.requests))
    variables['total_visits'] = query.scalar()
    variables['total_groups'] = Event.query.count()
    variables['total_invites'] = BuddyInvitation.query.count()
    # Maybe only count users who have logged in?
    variables['total_users'] = User.query.count()
    variables['courses'] = Course.query.all()
    return variables


@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', **get_stats())


@app.route("/admin/course/add", methods=['POST'])
@admin_required
def admin_add_course():
    name = form_get('name')
    check_empty(name, "Course Name")
    instructor = form_get('instructor')
    check_empty(instructor, "Professor Name")
    if not get_flashed_messages():
        course = Course(name=name, instructor=instructor)
        db.session.add(course)
        db.session.commit()
        flash("Added Course " + name)
    return redirect(url_for('admin_dashboard'))
    #return render_template('admin/dashboard.html', **get_stats())


@app.route("/admin/course/delete", methods=['POST'])
@admin_required
def admin_delete_course():
    course_ids = map(int, request.form.getlist('listcourse'))
    for course_id in course_ids:
        Course.query.filter_by(id=course_id).delete()
    db.session.commit()
    flash('Course deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/location/add", methods=['POST'])
@admin_required
def admin_add_location():
    name = form_get('name')
    check_empty(name, "Location Name")
    if not get_flashed_messages():
        loc = Location(name=name)
        db.session.add(loc)
        db.session.commit()
        flash("Added Course " + name)
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/location/delete", methods=['POST'])
@admin_required
def admin_delete_location():
    location_ids = map(int, request.form.getlist('listlocation'))
    for location_id in location_ids:
        Location.query.filter_by(id=location_id).delete()
    db.session.commit()
    flash('Location deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/users")
@admin_required
def admin_user_management():
    pass


@app.route("/admin/forums")
@admin_required
def admin_forum_management():
    pass


@app.route("/admin/stats")
@admin_required
def admin_stats():
    variables = {}
    variables['group_count'] = Event.query.count()
    variables['unique_visits'] = Visit.query.count()
    # This requires something with func.sum. Not sure what.
    variables['total_visits'] = Visit.query.sum(Visit.requests)
    variables['total_groups'] = Event.query.count()
    variables['total_invites'] = BuddyInvitation.query.count()
    # Maybe only count users who have logged in?
    variables['total_users'] = User.query.filter(User.activated == True).count()
    
    render_template('admin_stats.html', **variables)
