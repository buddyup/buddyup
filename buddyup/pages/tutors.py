from calendar import day_name as day_names
from flask import g, request, url_for, redirect, flash

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed

from wtforms.validators import required, Email, Optional
from wtforms.fields import TextField, RadioField, FieldList, TextAreaField
from wtforms.ext.sqlalchemy.fields import (QuerySelectMultipleField,
                                           QuerySelectField)

from buddyup.app import app
from buddyup.database import User, Course, Major, Location, db, Tutor, TutorCourse
from buddyup.util import sorted_languages, login_required
from buddyup.templating import render_template
from buddyup.photo import change_profile_photo, clear_images, ImageError

from buddyup.pages.form_profile import TutorApplicationForm

PHOTO_EXTS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff']
# Python 3: infinite loop because map() is lazy, use list(map(...))
# The next version of Flask-WTF will have a fix to be case-insensitive.
PHOTO_EXTS.extend(map(str.upper, PHOTO_EXTS))

def extract_names(records):
    return sorted(record.name for record in records)

def already_applied():
    return Tutor.query.join(User).filter(User.id==g.user.id).count() > 0

@app.route('/tutors/', methods=['GET', 'POST'])
@login_required
def tutor_application():
    if already_applied():
        return redirect(url_for('tutor_application_complete'))

    form = TutorApplicationForm()

    if form.validate_on_submit():

        application = Tutor()
        application.user_id = g.user.id

        for course in form.courses.data:
            application.courses.append(course)

        for language in form.languages.data:
            application.languages.append(language)

        # application.location = form.location.data
        # application.status = form.status.data
        # application.price = form.price.data
        # application.per = form.per.data

        db.session.add(application)
        db.session.commit()

        return redirect(url_for('tutor_application_complete'))
    else:
        return render_template('tutors/application.html', form=form, courses=Course.query.all())


@app.route('/tutors/applied', methods=['GET', 'POST'])
@login_required
def tutor_application_complete():
    return render_template('tutors/thankyou.html')

def tutors_for_course(course):
    user_ids = [t.user_id for t in course.tutors if t.approved]
    return list(User.query.filter(User.id.in_(user_ids)))
