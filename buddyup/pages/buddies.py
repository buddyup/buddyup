from flask import g, request, abort, redirect

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership,
                              Course, CourseMembership, db)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages


def extract_names(records):
    return sorted(record.name for record in records)


@app.route("/buddy/view/<user_name>")
@login_required
def buddy_view(user_name):
    if (user_name == g.user.user_name):
        majors = extract_names(g.user.majors)
        courses = extract_names(g.user.courses)
        languages = extract_names(g.user.languages)
        return render_template('my/profile.html',
                               buddy_record=g.user,
                               majors=majors,
                               courses=courses,
                               languages=languages,
                               is_buddy=False,
                               )
    else:
        buddy_record = User.query.filter_by(user_name=user_name).first_or_404()
        majors = extract_names(buddy_record.majors)
        languages = extract_names(buddy_record.languages)
        courses = extract_names(buddy_record.courses)
        is_buddy = buddy_record in g.user.buddies
        is_invited = buddy_record in g.user.sent_bud_inv
        #is_buddy = g.user.buddies.filter_by(id=buddy_record.id).count() == 1
        #is_invited = (BuddyInvitation.query.filter_by(receiver_id=g.user.id,
        #                                             sender_id=buddy_record.id)
        #                             .count() == 1)
        return render_template('buddy/view.html',
                               buddy_record=buddy_record,
                               majors=majors,
                               languages=languages,
                               courses=courses,
                               is_buddy=is_buddy,
                               is_invited=is_invited,
                               )


@app.route("/buddy/search")
@login_required
def buddy_search():
    courses = g.user.courses.all()
    majors = Major.query.all()
    languages = sorted_languages()
    locations = Location.query.order_by(Location.name).all()
    return render_template('buddy/search.html',
                           courses=courses,
                           majors=majors,
                           languages=languages,
                           locations=locations,
                           )


@app.route("/buddy/search_result")
@login_required
def buddy_search_results():
    name = args_get('name')
    major_id = args_get('major', convert=int)
    language_id = args_get('language', convert=int)
    location_id = args_get('location', convert=int)
    query = User.query
    query = query.order_by(User.full_name)
    if name:
        query = query.filter(User.full_name.ilike('%' + name + "%"))
    course_id = args_get('course', convert=int)
    # -1 -> all courses we're in
    if course_id == -1:
        query = query.filter(CourseMembership.c.course_id == Course.id,
                             CourseMembership.c.user_id == User.id)
    # != -1 -> one course (course_id)
    else:
        query = query.filter(CourseMembership.c.course_id == course_id,
                             CourseMembership.c.user_id == User.id)
    if major_id != -1:
        query = query.filter(MajorMembership.c.major_id == major_id,
                             MajorMembership.c.user_id == User.id)
    if language_id != -1:
        query = query.filter(LanguageMembership.c.language_id == language_id,
                             LanguageMembership.c.user_id == User.id)

    query = query.filter(User.id == location_id)
    query = query.filter(User.id != g.user.id)
    buddies = query.all()
    return render_template('buddy/search_result.html',
                           search_results=buddies)


@app.route('/buddy/unfriend/<user_name>')
def unfriend(user_name):
    user = g.user
    other_user = User.query.filter_by(user_name=user_name).first_or_404()
    if (user.buddies.filter_by(id=other_user.id).count() == 0 or
            other_user.buddies.filter_by(id=user.id).count() == 0):
        abort(404)
    else:
        user.buddies.remove(other_user)
        other_user.buddies.remove(user)
        db.session.commit()
        return redirect(request.referrer)
