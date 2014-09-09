from flask import url_for, redirect, g, request, session, make_response, flash

from buddyup.app import app
from buddyup.database import User
from buddyup.util import login_required, shuffled
from buddyup.templating import render_template
from buddyup.pages.profile import copy_form
from buddyup.pages.form_profile import ProfileCreateForm

@app.route('/start')
def start():
    # TODO: Add environment-driven options for login.
    return render_template('registration/start.html')


# @app.route('/dev/register')
# @login_required
# def view_registration_page():
#     # TODO: Remove this after development is complete.
#     return render_template('registration/register.html')


@app.route('/register', methods=['GET', 'POST'])
@login_required
def profile_create():
    form = ProfileCreateForm()

    if form.validate_on_submit():
        term_condition = request.form.getlist('term_condition')

        if term_condition == []:
            flash("Please agree to terms and conditions")
            return render_template('registration/register.html', form=form)
        else:
            copy_form(form)
            return redirect(url_for('registration_complete'))
    else:
        return render_template('registration/register.html', form=form)


@app.route('/done')
@login_required
def registration_complete():
    return render_template('registration/complete.html')


@app.route('/verify')
@login_required
def unverified():
    return render_template('registration/unverified.html')


@app.route('/terms')
def terms_and_conditions():
    return render_template('registration/terms_and_conditions.html')
