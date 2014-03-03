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
from buddyup.database import Course, Major, Location, Availability, db
from buddyup.util import sorted_languages, login_required, update_relationship
from buddyup.templating import render_template
from buddyup.photo import change_profile_photo, clear_images, ImageError
from buddyup.pages.form_profile import (ProfileCreateForm, ProfileUpdateForm,
                                        PhotoCreateForm, PhotoDeleteForm)
                                        


PHOTO_EXTS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff']
# Python 3: infinite loop because map() is lazy, use list(map(...))
# The next version of Flask-WTF will have a fix to be case-insensitive.
PHOTO_EXTS.extend(map(str.upper, PHOTO_EXTS))


@app.route('/setup/profile', methods=['GET', 'POST'])
@login_required
def profile_create():
    form = ProfileCreateForm()

    if form.validate_on_submit():
        term_condition = request.form.getlist('term_condition')
        print term_condition
        if term_condition == []:
            flash("Please check in the box")
            return render_template('setup/landing.html', form=form,
                            day_names=day_names,)
        else:
            copy_form(form)
            return redirect(url_for('suggestions'))
    else:
        return render_template('setup/landing.html',
                                form=form,
                                day_names=day_names,
                                )


@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def profile_edit():
    user = g.user
    if user.has_photos == True:
        form = ProfileUpdateForm()
    else:
        form = ProfileCreateForm()
    if not form.validate_on_submit():
        if request.method == 'GET':
            form.full_name.data = user.full_name
            form.facebook.data = user.facebook
            form.twitter.data = user.twitter
            form.email.data = user.email
            form.linkedin.data = user.linkedin
            form.bio.data = user.bio
            form.majors.data = user.majors.all()
            form.languages.data = user.languages.all()
            form.courses.data = user.courses.all()
            form.location.data = user.location

            times_to_choices = {
                (False, False): "none",
                (True, True): "all",
                (True, False): "am",
                (False, True): "pm",
                }
            times = {(time.day, time.time) for time in user.available}
            for i, field in enumerate(form.availability):
               am = (i, "am") in times
               pm = (i, "pm") in times
               field.data = times_to_choices[(am, pm)]

        return render_template('my/edit_profile.html',
                               form=form,
                               day_names=day_names,
                               )
    else:
        copy_form(form)
        return redirect(url_for('buddy_view', user_name=user.user_name))


def copy_form(form):
    user = g.user
    user.full_name = form.full_name.data
    user.location = form.location.data
    user.facebook = form.facebook.data
    user.twitter = form.twitter.data
    user.linkedin = form.linkedin.data
    user.bio = form.bio.data
    user.email = form.email.data
    
    AVAILABILITIES = {
        'am': ('am',),
        'pm': ('pm',),
        'all': ('am', 'pm'),
        'none': (),
    }
    Availability.query.filter_by(user_id=user.id).delete()
    for i, day in enumerate(form.availability):
        for time in AVAILABILITIES[day.data]:
            record = Availability(user_id=user.id,
                                  day=i,
                                  time=time)
            db.session.add(record)
    update_relationship(user.courses, form.courses.data)
    update_relationship(user.majors, form.majors.data)
    update_relationship(user.languages, form.languages.data)
    if form.photo.data:
#        for name in dir(form.photo):
#            app.logger.info("%s: %r", name, getattr(form.photo, name))
        storage = request.files[u"photo"]
        change_profile_photo(user, storage)
    user.initialized = True
    db.session.commit()

@app.route("/my/photo", methods=["GET", "POST"])
def profile_photo():
    form = PhotoCreateForm()
    delete_form = PhotoDeleteForm()
    if form.validate_on_submit():
        storage = request.files[u"photo"]
        try:
            change_profile_photo(g.user, storage)
        except ImageError:
            flash("Could not read photo file")
            app.logger.warn("uploaded image file for user %s could not be parsed",
                            g.user.user_name)
        else:
            db.session.commit()
            flash("Successfully changed photo")
        return redirect(url_for('home'))
    else:
        return render_template("my/photo.html",
                               form=form,
                               delete_form=delete_form)


@app.route("/my/photo/delete", methods=["POST"])
def profile_photo_delete():
    form = PhotoDeleteForm()
    if not form.validate():
        return redirect(url_for('home'))
    else:
        clear_images(g.user)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/my/profile/delete")
def profile_delete():
    delete_user(g.user)
    return redirect(url_for("logout"))
