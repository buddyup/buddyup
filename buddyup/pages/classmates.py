from flask import g, request, abort, redirect

from buddyup.app import app
from buddyup.database import (User, BuddyInvitation, Major, MajorMembership,
                              Language, LanguageMembership,
                              Course, CourseMembership, db,
                              Location, Action)
from buddyup.templating import render_template
from buddyup.util import login_required, args_get, sorted_languages, shuffled, track_activity

from collections import defaultdict

PAGE_SIZE=45

def extract_names(records):
    return sorted(record.name for record in records)

@app.route("/classmates/<user_name>")
@login_required
@track_activity
def buddy_view(user_name):
    classmate = g.user if user_name == g.user.user_name else User.query.filter_by(user_name=user_name).first_or_404()

    # Not our buddy if we're viewing ourselves or they aren't in our buddies list.
    myself = (user_name == g.user.user_name)
    is_buddy = (not myself) and (classmate in g.user.buddies)

    return render_template('buddy/view.html', classmate=classmate, is_buddy=is_buddy, myself=myself)


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



def annotate_buddies(classmates):
    classmates = list(classmates)
    buddy_ids = {buddy.id for buddy in g.user.buddies}
    for classmate in classmates:
        classmate.__dict__["is_buddy"] = (classmate.id in buddy_ids)
    return classmates



@app.route('/classmates/')
@app.route('/classmates/page/<int:page>')
@login_required
def list_classmates(page=1):
    return render_template('buddy/index.html', user=g.user, classmates=annotate_buddies(paginated_classmates(page)), everyone="selected")


@app.route('/classmates/buddies')
@app.route('/classmates/buddies/page/<int:page>')
@login_required
def list_buddies(page=1):
    buddies = g.user.buddies.order_by(User.full_name).paginate(page, per_page=PAGE_SIZE).items
    for buddy in buddies:
        buddy.__dict__["is_buddy"] = True # We're in 'Buddies' after all!
    return render_template('buddy/index.html', user=g.user, classmates=buddies, buddies="selected")


@app.route('/classmates/majors/')
@app.route('/classmates/majors/page/<int:page>')
@login_required
def list_classmates_by_major(page=1):
    classmates_by_major = classmates_query()\
                            .add_entity(Major)\
                            .filter(User.id == MajorMembership.columns['user_id'])\
                            .filter(MajorMembership.columns['major_id'] == Major.id)\
                            .order_by(Major.name)\
                            .paginate(page, per_page=PAGE_SIZE).items

    CLASSMATE = 0
    MAJOR = 1

    classmates = defaultdict(list)

    count = 0

    for classmate_by_major in classmates_by_major:
        if classmate_by_major[MAJOR].name == "Accounting":
            count+=1
        classmates[classmate_by_major[MAJOR].name].append(classmate_by_major[CLASSMATE])

    majors = sorted(classmates.keys())

    print majors

    print "Accounting majors on this pull? %s" % count

    return render_template('buddy/by_grouping.html', user=g.user, classmates=classmates, groupings=majors, major="selected")

@app.route('/classmates/languages/')
@app.route('/classmates/languages/page/<int:page>')
@login_required
def list_classmates_by_language(page=1):
    classmates = defaultdict(list)

    for classmate in annotate_buddies(paginated_classmates(page)):
        if classmate.languages:
            for language in classmate.languages:
                classmates[language.name].append(classmate)
        # If you don't indicate a language, we leave you out of this particular view.

    languages = sorted(classmates.keys())

    return render_template('buddy/by_grouping.html', user=g.user, classmates=classmates, groupings=languages, language="selected")


@app.route('/classmates/locations/')
@app.route('/classmates/locations/page/<int:page>')
@login_required
def list_classmates_by_location(page=1):
    classmates = defaultdict(list)

    for classmate in annotate_buddies(paginated_classmates(page)):
        classmates[classmate.location.name if classmate.location else "Unknown"].append(classmate)

    locations = sorted(classmates.keys())

    return render_template('buddy/by_grouping.html', user=g.user, classmates=classmates, groupings=locations, location="selected")


@app.route('/classmate/invite')
@login_required
def invite_friend():
    return render_template('buddy/invite_friend.html')
