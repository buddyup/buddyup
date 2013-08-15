from flask import g

from buddyup.app import app
from buddyup.database import Course, Visit, db
from buddyup.templating import render_template
from functools import partial, wraps


def admin_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if g.user and g.user.user_name == app.config.get("ADMIN_USER", u""):
            return f(*args, **kwargs)
        else:
            abort(403)
    return func


@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template('dashboard.html')


@app.route("/admin/course/add", methods=['POST', 'GET'])
@admin_required
def admin_add_course():
 
    if request.method == 'POST':
        get_int = partial(form_get, convert=int)
        # TODO: Change to include
        crn = get_int('crn')
        name = form_get('name')
        check_empty(name, "Course Name")
        subject = get_int('subject')
        number = get_int('number')
        course = Course(crn=crn,
                        name=name,
                        subject=subject,
                        number=number)
        db.session.add(course)
        db.session.commit()
        flash("Added Course " + name)
    return render_template('add_course.html')


@app.route("/admin/course/delete", methods=['POST', 'GET'])
@admin_required
def admin_delete_course():
    if request.method == 'POST':
        course_id = form_get('course_id', convert=int)
        course_record = Course.query.filter(Course.id == course_id).delete()
        db.session.commit()
        flash('Course deleted')
        return render_template('course_delete.html')
    else:
        return render_template('course_delete.html')


@app.route("/admin/stats")
@admin_required
def admin_stats():
    variables = {}
    variables['group_count'] = Group.query.count()
    variables['unique_visits'] = Visit.query.count()
    # This requires something with func.sum. Not sure what.
    variables['total_visits'] = Visit.query.sum(Visit.requests)
    variables['total_groups'] = Groups.query.count()
    variables['total_invites'] = Invites.query.count()
    # Maybe only count users who have logged in?
    variables['total_users'] = User.query.filter(User.activated == True).count()
    
    render_template('admin_stats.html', **variables)
