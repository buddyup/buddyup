from flask import url_for, redirect, g, request, session, make_response

from buddyup.app import app
from buddyup.database import User
from buddyup.util import login_required, shuffled
from buddyup.templating import render_template


@app.route('/start')
@login_required
def start():
    return render_template('registration/start.html')


@app.route('/register')
@login_required
def register():
    return render_template('registration/register.html')


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



# @app.route('/registration', methods=['GET', 'POST'])
# @login_required
# def register():
#     form = ProfileCreateForm()
#
#     if form.validate_on_submit():
#         term_condition = request.form.getlist('term_condition')
#         print term_condition
#         if term_condition == []:
#             flash("Please agree to terms and conditions")
#             return render_template('registration/landing.html', form=form,
#                             day_names=day_names,)
#         else:
#             copy_form(form)
#             return redirect(url_for('suggestions'))
#     else:
#         return render_template('profile/setup.html',
#                                 form=form,
#                                 classmate=g.user,
#                                 day_names=day_names,
#                                 )
