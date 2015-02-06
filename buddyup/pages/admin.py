# Python 3: Switch to io.StringIO
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import csv

from flask import (g, abort, get_flashed_messages, request, flash, redirect,
                   url_for, Response)

from sqlalchemy.sql import functions

from buddyup.app import app
from buddyup.database import (Course, Visit, User, BuddyInvitation, Tutor,
                              Location, Major, Event, Language, CourseMembership,
                              db)
from buddyup.templating import render_template
from buddyup.util import form_get, args_get, check_empty, email
from functools import wraps


def admin_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if app.config.get("BUDDYUP_ENABLE_ADMIN_ALL_USERS", False):
            # Every user has admin access.  Only for testing and development!
            return f(*args, **kwargs)
        if g.user and "buddyup.org" in g.user.email and g.user.email_verified:
            return f(*args, **kwargs)
        else:
            abort(403)
    return func


@app.route("/admin")
@admin_required
def admin_dashboard():
    variables = {}
    variables['group_count'] = Event.query.count()
    variables['unique_visits'] = Visit.query.count()
    query = db.session.query(functions.sum(Visit.requests))
    variables['total_visits'] = query.scalar()
    variables['total_groups'] = Event.query.count()
    variables['total_invites'] = BuddyInvitation.query.count()
    # Maybe only count users who have logged in?
    variables['total_users'] = User.query.count()
    variables['courses'] = Course.query.order_by(Course.name).all()
    variables['majors'] = Major.query.order_by(Major.name).all()
    variables['locations'] = Location.query.order_by(Location.name).all()
    variables['languages'] = Language.query.order_by(Language.name).all()
    variables['tutors'] = Tutor.query.order_by(Tutor.approved.desc()).all()
    variables['User'] = User
    return render_template('admin/dashboard.html', **variables)


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
    course_ids = map(int, request.form.getlist('courses'))
    for course_id in course_ids:
        Course.query.filter_by(id=course_id).delete()
    db.session.commit()
    flash('Course deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/course/roster")
@admin_required
def admin_roster():
    course_id = args_get('course', convert=int)
    course = Course.query.get_or_404(course_id)
    fake_file = StringIO()
    writer = csv.writer(fake_file)
    writer.writerow(["User name", "Full Name", "Email"])
    for student in course.users.all():
        user_name = student.user_name
        # Python 3: Don't encode
        full_name = student.full_name.encode('utf8')
        writer.writerow([user_name, full_name, student.email])
    return Response(fake_file.getvalue(), content_type="text/csv")


@app.route("/admin/update-tutors", methods=['POST'])
@admin_required
def admin_update_tutors():
    print request.form
    # Ouch, what a hack.
    approved_ids = []
    for k in request.form:
        approved_ids.append(int(k[k.find("_")+1:k.rfind("_")]))

    tutors = Tutor.query.all()
    for t in tutors:
        if t.id in approved_ids:
            t.approved = True
        else:
            t.approved = False
        db.session.add(t)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/tutors")
@admin_required
def admin_tutor_csv():
    tutors = Tutor.query.all()
    fake_file = StringIO()
    writer = csv.writer(fake_file)
    writer.writerow(["User name", "Full Name", "Email", "Courses", "Languages"])
    for t in tutors:
        student = User.query.get_or_404(t.user_id)
        user_name = student.user_name
        courses = ", ".join([c.name for c in t.courses])
        languages = ", ".join([l.name for l in t.languages])
        # Python 3: Don't encode
        full_name = student.full_name.encode('utf8')
        writer.writerow([user_name, full_name, student.email, courses, languages])
    return Response(fake_file.getvalue(), content_type="text/csv")


@app.route("/admin/course/aggregate")
@admin_required
def admin_aggregates():
    courses = Course.query.all()
    fake_file = StringIO()
    writer = csv.writer(fake_file)
    writer.writerow(["Course Name", "Number of Students"])
    for course in courses:
        writer.writerow([course.name, course.users.count()])
    return Response(fake_file.getvalue(), content_type="text/csv")


@app.route("/admin/email/list")
@admin_required
def admin_email_list():
    # Only users that are in a class this term?
    users = (User.query.filter(CourseMembership.c.user_id == User.id)
                       .distinct().all())
    emails = ("{} <{}>".format(user.full_name, email(user))
              for user in users)
    return Response(", ".join(emails), content_type="text/plain")


@app.route("/admin/location/add", methods=['POST'])
@admin_required
def admin_add_location():
    name = form_get('location')
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
    location_ids = map(int, request.form.getlist('location'))
    for location_id in location_ids:
        Location.query.filter_by(id=location_id).delete()
    db.session.commit()
    flash('Location deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/major/add", methods=['POST'])
@admin_required
def admin_add_major():
    name = form_get('major')
    check_empty(name, "Major Name")
    if not get_flashed_messages():
        major = Major(name=name)
        db.session.add(major)
        db.session.commit()
        flash("Added Course " + name)
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/major/delete", methods=['POST'])
@admin_required
def admin_delete_major():
    major_ids = map(int, request.form.getlist('majors'))
    for major_id in major_ids:
        Major.query.filter_by(id=major_id).delete()
    db.session.commit()
    flash('Majors deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/language/add", methods=['POST'])
@admin_required
def admin_add_language():
    name = form_get('language')
    check_empty(name, "Language Name")
    if not get_flashed_messages():
        language = Language(name=name)
        db.session.add(language)
        db.session.commit()
        flash("Added Language " + name)
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/language/delete", methods=['POST'])
@admin_required
def admin_delete_language():
    language_ids = map(int, request.form.getlist('languages'))
    for language_id in language_ids:
        Language.query.filter_by(id=language_id).delete()
    db.session.commit()
    flash('Languages deleted')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/users")
@admin_required
def admin_user_management():
    users = User.query.all()
    return render_template('admin/userManagement.html', users=users)


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
