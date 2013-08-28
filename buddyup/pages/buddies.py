from flask import g, request, abort, redirect

from buddyup.app import app
from buddyup.database import (User, Buddy, BuddyInvitation, CourseMembership,
                              Course, Major, MajorMembership, db)
from buddyup.templating import render_template
from buddyup.util import login_required, form_get
from buddyup.database import User

@app.route("/buddy/view/<user_name>")
@login_required
def buddy_view(user_name):
    if (user_name == g.user.user_name):
        majors = [major.name for major in g.user.majors]
        return render_template('my/profile.html',
                               buddy_record=g.user,
                               majors=majors,
                               is_buddy=False)
    else:
        buddy_record = User.query.filter_by(user_name=user_name).first_or_404()
        majors = [major.name for major in g.user.majors]
        is_buddy = g.user.buddies.filter_by(id=buddy_record.id).count() == 1
        is_invited = (BuddyInvitation.query.filter_by(receiver_id=g.user.id,
                                                     sender_id=buddy_record.id)
                                     .count() == 1)
        return render_template('buddy/view.html',
                               buddy_record=buddy_record,
                               majors=majors,
                               is_buddy=is_buddy,
                               is_invited=is_invited)


@app.route("/buddy/search")
@login_required
def buddy_search():
    courses = g.user.courses.all()
    return render_template('buddy/search.html',
                           courses=courses,
                           majors=Major.query.order_by(Major.name).all())


@app.route("/buddy/search_result", methods=['POST'])
@login_required
def buddy_search_results():
    name = form_get('name')
    #major = args_get('major')
    query = User.query
    query = query.order_by(User.full_name)
    if name:
        query = query.filter(User.full_name.ilike('%' + name + "%"))
    course_ids = map(int, request.form.getlist('course'))
    if course_ids:
        query = query.filter(CourseMembership.c.course_id.in_(course_ids))
    else:
        course_ids = query.filter(CourseMembership.c.course_id == Course.id,
                                  CourseMembership.c.user_id == User.id)
    #if major != -1:
        #query = query.filter(MajorMembership.c.major_id == Major.id,
                             #MajorMembership.c.user_id == User.id)
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
