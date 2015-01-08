import hashlib
from flask import url_for, redirect, g, request, session, make_response, flash

from buddyup.app import app
from buddyup.database import User, db
from buddyup.util import login_required, shuffled, send_out_verify_email
from buddyup.templating import render_template
from buddyup.pages.profile import update_current_user
from buddyup.pages.form_profile import ProfileCreateForm

@app.route('/start')
def start():
    # TODO: Add environment-driven options for login.
    return render_template('registration/start.html')


@app.route('/register', methods=['GET', 'POST'])
@login_required
def profile_create():
    # Don't let already-registered users back to this screen
    # TODO: Make this a decorator. The Start and Done screens
    # could also use this, though not as critically.
    if g.user and g.user.initialized:
        return redirect('home')

    form = ProfileCreateForm()

    if form.validate_on_submit():
        term_condition = request.form.getlist('term_condition')

        if term_condition == []:
            flash("Please agree to terms and conditions")
            return render_template('registration/register.html', form=form)
        else:
            update_current_user(form)
            if not g.user.email_verify_code or g.user.email_verify_code == "":
                m = hashlib.sha1()
                m.update("Verify email for %s" % g.user.user_name)
                g.user.email_verify_code = u"%s" % m.hexdigest()
                db.session.commit()

            send_out_verify_email(g.user)
            return redirect(url_for('home'))
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
    return render_template('registration/terms.html')

@app.route('/privacy')
def privacy_policy():
    return render_template('registration/privacy.html')
