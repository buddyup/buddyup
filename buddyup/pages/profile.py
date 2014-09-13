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
from buddyup.database import Course, Major, Location, db
from buddyup.util import sorted_languages, login_required, update_relationship
from buddyup.templating import render_template
from buddyup.photo import change_profile_photo, clear_images, ImageError
from buddyup.pages.form_profile import (ProfileCreateForm, ProfileUpdateForm,
                                        PhotoCreateForm, PhotoDeleteForm)
                                        


PHOTO_EXTS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff']
# Python 3: infinite loop because map() is lazy, use list(map(...))
# The next version of Flask-WTF will have a fix to be case-insensitive.
PHOTO_EXTS.extend(map(str.upper, PHOTO_EXTS))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = g.user

    if user.has_photos == True:
        form = ProfileUpdateForm()
    else:
        form = ProfileCreateForm()

    if form.validate_on_submit():
        update_current_user(form)
        return redirect(url_for('buddy_view', user_name=user.user_name))
    else:

        if request.method == 'GET':
            form.full_name.data = user.full_name
            form.facebook.data = user.facebook
            form.twitter.data = user.twitter
            form.email.data = user.email
            form.linkedin.data = user.linkedin
            form.bio.data = user.bio
            form.majors.data = user.majors.all()
            form.languages.data = user.languages.all()
            form.location.data = user.location

    return render_template('profile/edit.html', form=form, classmate=user)


def update_current_user(form):
    user = g.user
    user.full_name = form.full_name.data
    user.location = form.location.data
    user.facebook = form.facebook.data
    user.twitter = form.twitter.data
    user.linkedin = form.linkedin.data
    user.bio = form.bio.data
    user.email = form.email.data

    update_relationship(user.majors, form.majors.data)
    update_relationship(user.languages, form.languages.data)

    if form.photo.data:
        storage = request.files[u"photo"]
        change_profile_photo(user, storage)

    user.initialized = True
    db.session.commit()

@app.route("/profile/photo", methods=["GET", "POST"])
@login_required
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
        return redirect(url_for('buddy_view', user_name=g.user.user_name))
    else:
        return render_template("profile/photo.html",
                               form=form,
                               delete_form=delete_form, classmate=g.user)


@app.route("/profile/photo/delete", methods=["POST"])
@login_required
def profile_photo_delete():
    form = PhotoDeleteForm()
    if not form.validate():
        return redirect(url_for('home'))
    else:
        clear_images(g.user)
        db.session.commit()
        return redirect(url_for('home'))


