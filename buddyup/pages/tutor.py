from calendar import day_name as day_names
from flask import g, request, url_for, redirect, flash

#from flask.ext

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed

from wtforms.validators import required, Email, Optional
from wtforms.fields import TextField, RadioField, FieldList, TextAreaField
from wtforms.ext.sqlalchemy.fields import (QuerySelectMultipleField,
                                           QuerySelectField)

from buddyup.app import app
from buddyup.database import User, Course, Major, Location, Availability, db
from buddyup.util import sorted_languages, login_required
from buddyup.templating import render_template
from buddyup.photo import change_profile_photo, clear_images, ImageError
from buddyup.pages.form_profile import (TutorProfileUpdateForm,
                                        TutorProfileCreateForm)

PHOTO_EXTS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff']
# Python 3: infinite loop because map() is lazy, use list(map(...))
# The next version of Flask-WTF will have a fix to be case-insensitive.
PHOTO_EXTS.extend(map(str.upper, PHOTO_EXTS))

def extract_names(records):
    return sorted(record.name for record in records)

@app.route('/setup/create_tutor', methods=['GET', 'POST'])
@login_required
def profile_tutor_create():
    if g.user.tutor == True:
        flash("You are being a tutor")
        return redirect(url_for('home'))
    else:
        form = ProfileTutorUpdateForm()
        form.full_name.data = g.user.full_name
    if form.validate_on_submit():
        copy_form_tutor(form)
        return redirect(url_for('tutor/view.html'))
    else:
        return render_template('setup/tutor.html',
                                form=form,
                                day_names = day_names)

def copy_form_tutor(form):
    tutor = Tutor(user_name = g.user.user_name, bio = form.bio.data)

    db.session.add(tutor)
    db.session.commit()

    AVAILABILITIES = {
        'am': ('am',),
        'pm': ('pm',),
        'all': ('am', 'pm'),
        'none': (),
    }

    AvailabilityTutor.query.filter_by(tutor_id=tutor.id).delete()
    for i, day in enumerate(form.availability):
        for time in AVAILABILITIES[day.data]:
            record = AvailabilityTutor(tutor_id=tutor.id,
                                        day=i,
                                      time=time)
            db.session.add(record)

    '''course_id = Course.query.filter_by(name = form.courses_tutoring.data)'''

    update_relationship(tutor.subject_tutoring, form.subjects.data)
    update_relationship(tutor.languages, form.languages.data)
    if form.photo.data:
#        for name in dir(form.photo):
#            app.logger.info("%s: %r", name, getattr(form.photo, name))
        storage = request.files[u"photo"]
        change_profile_photo(tutor, storage)
    g.user.tutor = True
    db.session.commit()

@app.route("/tutor/view/<user_name>")
@login_required
def profile_tutor(user_name):
    buddy_record = User.query.filter_by(user_name=user_name).first_or_404()
    if buddy_record.tutor == False:
        flash("You are not applying for tutor")
        return redirect(url_for('profile_tutor_create'))
    else:
        tutor = Tutor.query.filter_by(user_name = user_name).first_or_404()
        majors = extract_names(buddy_record.majors)
        languages = extract_names(buddy_record.languages)
        subjects_tutoring = extract_names(tutor.subject_tutoring)
        bio = extract_names(tutor.bio)
        return render_template('tutor/view.html',
                                buddy_record = buddy_record,
                                majors = majors,
                                languages = languages,
                                subject_tutoring = subjects_tutoring)


'''@app.route("/tutor/delete/<user_name")
@login_required
def profile_delete(user_name):
    buddy_record = User.query.filter_by(user_name = user_name).first_or_404()
    buddy_record.tutor = False
    tutor = Tutor.query.filter_by(user_name=user_name).first_or_404()
    db.session'''