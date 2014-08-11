from flask import g, request, abort, redirect

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership,
                              Course, CourseMembership, db,
                              Location, Action)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages, shuffled, track_activity

from collections import defaultdict


@app.route("/courses/<id>")
@login_required
@track_activity
def course_view(id):
    course = Course.query.get_or_404(id)
    followers = course.users.filter(User.has_photos == True)
    return render_template('courses/view.html', course=course, followers=followers)


@app.route('/courses')
@login_required
def list_courses():
    courses = Course.query.order_by(Course.name).all()
    return render_template('courses/index.html', user=g.user, courses=courses, all_courses="selected")


@app.route("/courses/following")
@login_required
@track_activity
def my_courses():
    return render_template('courses/index.html', courses=g.user.courses.order_by(Course.name), following="selected")


@app.route('/courses/majors')
@login_required
def list_courses_by_major():
    courses = Course.query.order_by(Course.name).all()
    return render_template('courses/index.html', user=g.user, courses=courses, major="selected")

@app.route('/courses/<id>/followers')
@login_required
def course_followers(id):
    # TODO: Make this real
    return render_template('courses/followers.html', course=Course.query.get_or_404(id))




