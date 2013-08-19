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
    return render_template('admin/dashboard.html')


@app.route("/admin/course/add", methods=['POST', 'GET'])
@admin_required
def admin_add_course():
    name = form_get('name')
    check_empty(name, "Course Name")
    professor = form_get('professor')
    check_empty(professor, "Professor Name")
    if not get_flash_messages():
        course = Course(name=name, professor=professor)
        db.session.add(course)
        db.session.commit()
        flash("Added Course " + name)
    return render_template('admin/dashboard.html')


@app.route("/admin/course/delete", methods=['POST', 'GET'])
@admin_required
def admin_delete_course():
    course_ids = map(int, request.form.getlist('courselist'))
    for course_id in course_ids:
        Course.query.filter_by(id=course_id).delete()
    db.session.commit()
    flash('Course deleted')
    return render_template('.html')



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
    variables['group_count'] = Group.query.count()
    variables['unique_visits'] = Visit.query.count()
    # This requires something with func.sum. Not sure what.
    variables['total_visits'] = Visit.query.sum(Visit.requests)
    variables['total_groups'] = Groups.query.count()
    variables['total_invites'] = Invites.query.count()
    # Maybe only count users who have logged in?
    variables['total_users'] = User.query.filter(User.activated == True).count()
    
    render_template('admin_stats.html', **variables)
