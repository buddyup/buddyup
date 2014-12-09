from flask import g, request, abort, redirect, url_for

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership,
                              Course, CourseMembership, db,
                              Location, Action, Event)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages, shuffled, track_activity

from buddyup.pages.classmates import PAGE_SIZE
from buddyup.pages.tutors import tutors_for_course

from collections import defaultdict



from datetime import date, timedelta

def upcoming_events(course):
    """
    Events for a given Course from today onward.
    We return a query that you can limit as you see fit.
    """
    yesterday = date.today() - timedelta(days=1)
    return Event.query.join(Course)\
            .filter(Course.id==course.id)\
            .filter(Event.start > yesterday)\
            .order_by(Event.start)


@app.route("/courses/<id>")
@login_required
@track_activity
def course_view(id):
    course = Course.query.get_or_404(id)
    followers = course.users.filter(User.has_photos == True)
    events = upcoming_events(course).limit(2)
    tutors = tutors_for_course(course)

    return render_template('courses/view.html', user=g.user, course=course, followers=followers, events=events, tutors=tutors)


@app.route('/courses')
@login_required
def list_courses():
    courses = Course.query.order_by(Course.name).all()
    return render_template('courses/index.html', user=g.user, courses=courses, all_courses="selected")


@app.route("/courses/following")
@login_required
@track_activity
def my_courses():
    return render_template('courses/index.html', user=g.user, courses=g.user.courses.order_by(Course.name), following="selected")


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


@app.route('/courses/<id>/unfollow', methods=['POST'])
@login_required
def unfollow_course(id):
    course = Course.query.get_or_404(id)

    if course in g.user.courses:
        g.user.courses.remove(course)
        db.session.commit()

    return redirect(request.referrer)

@app.route('/courses/<id>/follow', methods=['POST'])
@login_required
def follow_course(id):
    course = Course.query.get_or_404(id)

    if course not in g.user.courses:
        g.user.courses.append(course)
        db.session.commit()

    return redirect(request.referrer)


#--------------------------------------------------------------------
# Course Follower stuff below
#--------------------------------------------------------------------
# TODO: This is clearly a cut-n-paste job from classmates.py, with
# some modifications. Find a better way to do this where this crazy
# duplication isn't necessary.
#--------------------------------------------------------------------

def coursemates_query(course_id):
    """
    Return EVERYONE taking the course.
    This returns a query object which you can refine further.
    """
    return User.query.filter(User.courses.any(Course.id==course_id))\
            .filter(User.has_photos == True)\
            .filter(User.id != g.user.id)


def paginated_coursemates(course_id, page=1):
    return coursemates_query(course_id).paginate(page, per_page=PAGE_SIZE).items


def mark_buddies(classmates):
    classmates = list(classmates)
    buddy_ids = {buddy.id for buddy in g.user.buddies}
    for classmate in classmates:
        classmate.__dict__["is_buddy"] = (classmate.id in buddy_ids)
    return classmates


def mark_buddies_in_group(classmates_by_group):
    buddy_ids = {buddy.id for buddy in g.user.buddies}
    for classmate, group in classmates_by_group:
        classmate.__dict__["is_buddy"] = (classmate.id in buddy_ids)
    return classmates_by_group



@app.route('/courses/<int:course_id>/followers/')
@app.route('/courses/<int:course_id>/followers/page/<int:page>')
@login_required
def list_coursemates(course_id, page=1):
    course = Course.query.get_or_404(course_id)

    link_next = None
    try:
        if len(coursemates_query(course_id).paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates', course_id=course_id, page=page+1)
    except:
        pass
    link_prev = url_for('list_coursemates', course_id=course_id, page=page-1) if page > 1 else None

    return render_template('courses/followers/index.html', user=g.user, course=course, classmates=mark_buddies(paginated_coursemates(course_id, page)), everyone="selected", next=link_next, prev=link_prev)


@app.route('/courses/<int:course_id>/followers/buddies')
@app.route('/courses/<int:course_id>/followers/buddies/page/<int:page>')
@login_required
def list_buddies_in_course(course_id, page=1):
    course = Course.query.get_or_404(course_id)

    link_next = None
    try:
        if len(g.user.buddies.order_by(User.full_name).paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_buddies_in_course', course_id=course_id, page=page+1)
    except:
        pass
    link_prev = url_for('list_buddies_in_course', course_id=course_id, page=page-1) if page > 1 else None

    buddies = g.user.buddies.order_by(User.full_name).paginate(page, per_page=PAGE_SIZE).items
    for buddy in buddies:
        buddy.__dict__["is_buddy"] = True # We're in 'Buddies' after all!
    return render_template('courses/followers/index.html', user=g.user, course=course, classmates=buddies, buddies="selected", next=link_next, prev=link_prev)


def list_by_group(grouped_classmates, **kwargs):
    grouped_classmates = mark_buddies_in_group(grouped_classmates)

    classmates = defaultdict(list)

    for classmate, group in grouped_classmates:
        classmates[group.name].append(classmate)

    groups = sorted(classmates.keys())

    return render_template('courses/by_grouping.html', user=g.user, classmates=classmates, groupings=groups, **kwargs)


@app.route('/courses/<int:course_id>/followers/majors/')
@app.route('/courses/<int:course_id>/followers/majors/page/<int:page>')
@login_required
def list_coursemates_by_major(course_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_major = coursemates_query(course_id)\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .order_by(Major.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .order_by(Major.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_major', course_id=course_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_major', course_id=course_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_major, course=course, major="selected", group_list=Major.query.order_by('name').all(), next=link_next, prev=link_prev)


@app.route('/courses/<int:course_id>/followers/majors/<int:major_id>/')
@app.route('/courses/<int:course_id>/followers/majors/<int:major_id>/page/<int:page>')
@login_required
def list_coursemates_by_single_major(course_id, major_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_major = coursemates_query(course_id)\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .filter(Major.id == major_id)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .filter(Major.id == major_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_single_major', course_id=course_id, major_id=major_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_single_major', course_id=course_id, major_id=major_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_major, course=course, major="selected", next=link_next, prev=link_prev)


@app.route('/courses/<int:course_id>/followers/languages/')
@app.route('/courses/<int:course_id>/followers/languages/page/<int:page>')
@login_required
def list_coursemates_by_language(course_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_language = coursemates_query(course_id)\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .order_by(Language.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .order_by(Language.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_language', course_id=course_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_language', course_id=course_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_language, course=course, language="selected", group_list=Language.query.order_by('name').all(), next=link_next, prev=link_prev)


@app.route('/courses/<int:course_id>/followers/languages/<int:language_id>/')
@app.route('/courses/<int:course_id>/followers/languages/<int:language_id>/page/<int:page>')
@login_required
def list_coursemates_by_single_language(course_id, language_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_language = coursemates_query(course_id)\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .filter(Language.id == language_id)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .filter(Language.id == language_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_single_language', course_id=course_id, language_id=language_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_single_language', course_id=course_id, language_id=language_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_language, course=course, language="selected", next=link_next, prev=link_prev)


@app.route('/courses/<int:course_id>/followers/locations/')
@app.route('/courses/<int:course_id>/followers/locations/page/<int:page>')
@login_required
def list_coursemates_by_location(course_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_location = coursemates_query(course_id)\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .order_by(Location.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .order_by(Location.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_location', course_id=course_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_location', course_id=course_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_location, course=course, location="selected", group_list=Location.query.order_by('name').all(), next=link_next, prev=link_prev)



@app.route('/courses/<int:course_id>/followers/locations/<int:location_id>/')
@app.route('/courses/<int:course_id>/followers/locations/<int:location_id>/page/<int:page>')
@login_required
def list_coursemates_by_single_location(course_id, location_id, page=1):
    course = Course.query.get_or_404(course_id)

    classmates_by_location = coursemates_query(course_id)\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .filter(Location.id == location_id)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(coursemates_query(course_id)\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .filter(Location.id == location_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_coursemates_by_single_location', course_id=course_id, location_id=location_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_coursemates_by_single_location', course_id=course_id, location_id=location_id, page=page-1) if page > 1 else None


    return list_by_group(classmates_by_location, course=course, location="selected", next=link_next, prev=link_prev)
