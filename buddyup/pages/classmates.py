from flask import g, request, abort, redirect, url_for

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership, Tutor,
                              Course, CourseMembership, db,
                              Location, Action)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages, shuffled, track_activity
from buddyup.pages.buddyinvitations import clear_buddy_invites
from collections import defaultdict

PAGE_SIZE=45

def extract_names(records):
    return sorted(record.name for record in records)

@app.route("/classmates/<user_name>")
@login_required
@track_activity
def buddy_view(user_name):
    classmate = g.user if user_name == g.user.user_name else User.query.filter_by(user_name=user_name).first_or_404()
    tutor = list(Tutor.query.filter(Tutor.approved==True).filter(Tutor.user_id==classmate.id).all())
    if len(tutor) > 0:
        tutor_for = tutor[0].courses.all()
    else:
        tutor_for = []

    # Not our buddy if we're viewing ourselves or they aren't in our buddies list.
    myself = (user_name == g.user.user_name)
    is_buddy = (not myself) and (classmate in g.user.buddies)
    is_invited = (not myself) and BuddyInvitation.query.filter(BuddyInvitation.sender == g.user, BuddyInvitation.receiver == classmate).count() > 0

    return render_template('buddy/view.html', classmate=classmate, is_buddy=is_buddy, is_invited=is_invited, myself=myself, tutor_for=tutor_for)


@app.route("/classmates/search")
@login_required
def buddy_search():
    courses = g.user.courses.all()
    majors = Major.query.all()
    languages = sorted_languages()
    locations = Location.query.order_by(Location.name).all()
    buddies = set(g.user.buddies)
    general = set()
    for course in courses:
        for user in course.users.filter(User.id != g.user.id):
            if user not in buddies:
                general.add(user)
    classmates = shuffled(general) + shuffled(buddies)

    return render_template('buddy/search.html',
                           courses=courses,
                           majors=majors,
                           languages=languages,
                           locations=locations,
                           classmates=classmates,
                           )


@app.route("/classmates/search_result")
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
    if location_id != -1:
        query = query.filter(User.location_id == location_id)

    query = query.filter(User.id != g.user.id)
    buddies = query.all()
    return render_template('buddy/search_result.html',
                           search_results=buddies)


@app.route('/classmates/<current_name>/buddies/<user_name>', methods=['POST'])
def unfriend(current_name, user_name):
    # We're only allowed to act on our own friends.
    if g.user.user_name != current_name: abort(404)

    user = g.user
    other_user = User.query.filter_by(user_name=user_name).first_or_404()
    if (user.buddies.filter_by(id=other_user.id).count() == 0 or
            other_user.buddies.filter_by(id=user.id).count() == 0):
        abort(404)
    else:
        user.buddies.remove(other_user)
        other_user.buddies.remove(user)
        db.session.commit()

        # Delete relationship both ways.
        clear_buddy_invites(g.user.id, other_user.id)
        clear_buddy_invites(other_user.id, g.user.id)

        return redirect(request.referrer)


def classmates_query():
    """
    Return all of 'my' classmates. (People I share a class with.)
    This returns a query object which you can refine further.
    """
    #TODO: Tune this. It's supposed to generate two queries but seems to generate many more.
    course_IDs = [c.id for c in User.query.get(g.user.id).courses]
    return User.query.filter(User.courses.any(Course.id.in_( course_IDs )))\
            .filter(User.has_photos == True)\
            .filter(User.id != g.user.id)


def paginated_classmates(page=1):
    return classmates_query().paginate(page, per_page=PAGE_SIZE).items


def annotate_classmates(classmates):
    classmates = list(classmates)
    invited_classmate_ids = {invite.receiver_id for invite in g.user.buddy_invitations_sent}
    buddy_ids = {buddy.id for buddy in g.user.buddies}
    for classmate in classmates:
        classmate.__dict__["invited"] = (classmate.id in invited_classmate_ids)
        classmate.__dict__["is_buddy"] = (classmate.id in buddy_ids)
    return classmates


def annotate_classmates_in_group(classmates_by_group):
    invited_classmate_ids = {invite.receiver_id for invite in g.user.buddy_invitations_sent}
    buddy_ids = {buddy.id for buddy in g.user.buddies}
    for classmate, group in classmates_by_group:
        classmate.__dict__["invited"] = (classmate.id in invited_classmate_ids)
        classmate.__dict__["is_buddy"] = (classmate.id in buddy_ids)
    return classmates_by_group



@app.route('/classmates/')
@app.route('/classmates/page/<int:page>')
@login_required
def list_classmates(page=1):
    filter_name = "Everyone"
    link_next = None
    try:
        if len(annotate_classmates(paginated_classmates(page+1))) > 0:
            link_next = url_for('list_classmates', page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates', page=page-1) if page > 1 else None

    return render_template('buddy/index.html', filter_name=filter_name,user=g.user, classmates=annotate_classmates(paginated_classmates(page)), everyone="selected", next=link_next, prev=link_prev)


@app.route('/classmates/buddies')
@app.route('/classmates/buddies/page/<int:page>')
@login_required
def list_buddies(page=1):
    link_next = None
    filter_name = "Buddies"
    try:
        if len(g.user.buddies.order_by(User.full_name).paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates', page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates', page=page-1) if page > 1 else None

    buddies = g.user.buddies.order_by(User.full_name).paginate(page, per_page=PAGE_SIZE).items
    for buddy in buddies:
        buddy.__dict__["is_buddy"] = True # We're in 'Buddies' after all!
    return render_template('buddy/index.html', user=g.user, filter_name=filter_name, classmates=buddies, buddies="selected", next=link_next, prev=link_prev)


def list_by_group(grouped_classmates, **kwargs):
    grouped_classmates = annotate_classmates_in_group(grouped_classmates)

    classmates = defaultdict(list)

    for classmate, group in grouped_classmates:
        classmates[group.name].append(classmate)

    groups = sorted(classmates.keys())

    return render_template('buddy/by_grouping.html', user=g.user, classmates=classmates, groupings=groups, **kwargs)


@app.route('/classmates/majors/')
@app.route('/classmates/majors/page/<int:page>')
@login_required
def list_classmates_by_major(page=1):
    filter_name = "Major"
    classmates_by_major = classmates_query()\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .order_by(Major.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .order_by(Major.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_major', page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates_by_major', page=page-1) if page > 1 else None

    return list_by_group(classmates_by_major, filter_name=filter_name, major="selected", group_list=Major.query.order_by('name').all(), next=link_next, prev=link_prev)


@app.route('/classmates/majors/<int:major_id>/')
@app.route('/classmates/majors/<int:major_id>/page/<int:page>')
@login_required
def list_classmates_by_single_major(major_id, page=1):
    filter_name = "Major"
    classmates_by_major = classmates_query()\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .filter(Major.id == major_id)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .filter(Major.id == major_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_single_major', major_id=major_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates_by_single_major', major_id=major_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_major,  filter_name=filter_name, major="selected", next=link_next, prev=link_prev)


@app.route('/classmates/languages/')
@app.route('/classmates/languages/page/<int:page>')
@login_required
def list_classmates_by_language(page=1):
    filter_name = "Language"
    classmates_by_language = classmates_query()\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .order_by(Language.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .order_by(Language.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_language', page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates_by_language', page=page-1) if page > 1 else None

    return list_by_group(classmates_by_language,  filter_name=filter_name, language="selected", group_list=Language.query.order_by('name').all(), next=link_next, prev=link_prev)


@app.route('/classmates/languages/<int:language_id>/')
@app.route('/classmates/languages/<int:language_id>/page/<int:page>')
@login_required
def list_classmates_by_single_language(language_id, page=1):
    filter_name = "Language"
    classmates_by_language = classmates_query()\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .filter(Language.id == language_id)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Language)\
                            .filter(User.id == LanguageMembership.columns['user_id'])\
                            .filter(LanguageMembership.columns['language_id'] == Language.id)\
                            .filter(Language.id == language_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_single_language', language_id=language_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates_by_single_language', language_id=language_id, page=page-1) if page > 1 else None

    return list_by_group(classmates_by_language, filter_name=filter_name, language="selected", next=link_next, prev=link_prev)


@app.route('/classmates/locations/')
@app.route('/classmates/locations/page/<int:page>')
@login_required
def list_classmates_by_location(page=1):
    filter_name = "Location"
    classmates_by_location = classmates_query()\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .order_by(Location.name)\
                            .paginate(page, per_page=PAGE_SIZE).items
    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .order_by(Location.name)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_location', page=page+1)
    except:
        pass


    link_prev = url_for('list_classmates_by_location', page=page-1) if page > 1 else None

    return list_by_group(classmates_by_location, filter_name=filter_name, location="selected", group_list=Location.query.order_by('name').all(), next=link_next, prev=link_prev)



@app.route('/classmates/locations/<int:location_id>/')
@app.route('/classmates/locations/<int:location_id>/page/<int:page>')
@login_required
def list_classmates_by_single_location(location_id, page=1):
    filter_name = "Location"
    classmates_by_location = classmates_query()\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .filter(Location.id == location_id)\
                            .paginate(page, per_page=PAGE_SIZE).items

    link_next = None
    try:
        if len(classmates_query()\
                            .add_entity(Location)\
                            .filter(User.location_id==Location.id)\
                            .filter(Location.id == location_id)\
                            .paginate(page+1, per_page=PAGE_SIZE).items) > 0:
            link_next = url_for('list_classmates_by_single_location', location_id=location_id, page=page+1)
    except:
        pass

    link_prev = url_for('list_classmates_by_single_location', location_id=location_id, page=page-1) if page > 1 else None


    return list_by_group(classmates_by_location, filter_name=filter_name, location="selected", next=link_next, prev=link_prev)


@app.route('/classmate/invite')
@login_required
def invite_friend():
    return render_template('buddy/invite_friend.html')
