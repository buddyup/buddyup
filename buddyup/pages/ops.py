from functools import wraps
from buddyup.app import app
from buddyup.database import (Course, Visit, User, BuddyInvitation,
                              Location, Major, Event, Language, CourseMembership,
                              Operator,
                              db)
from flask import Flask, redirect, request, render_template, flash, session

from flask.ext import admin
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import helpers, expose

from wtforms import form, fields, validators

import hashlib

OPERATOR_ID = 'operator_id'


class OperatorLoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self):
        operator = self.get_operator()

        #TODO: Add pages to handle a bad login.
        if operator is None:
            raise validators.ValidationError('Invalid login')

        if hashlib.sha256(self.password.data).hexdigest() != operator.password:
            raise validators.ValidationError('Invalid password')
        
        return operator

    def get_operator(self):
        return db.session.query(Operator).filter_by(login=self.login.data).first()

    def __repr__(self):
        return '%s' % self.login


def current_operator():
    if not OPERATOR_ID in session:
        return Operator()
        
    this_operator = Operator.query.get(session[OPERATOR_ID])
    
    if this_operator:
        this_operator.authenticated = True
        return this_operator
    else:
        return Operator()
    
class AuthenticatedView(ModelView):

    def is_accessible(self):
        return current_operator().is_authenticated()

admin = Admin(app, url="/ops", name="BuddyUp Operations")

admin.add_view(AuthenticatedView(User, db.session))
admin.add_view(AuthenticatedView(BuddyInvitation, db.session, "Invitation"))
admin.add_view(AuthenticatedView(Event, db.session))
admin.add_view(AuthenticatedView(Course, db.session))
admin.add_view(AuthenticatedView(Major, db.session))
admin.add_view(AuthenticatedView(Location, db.session))
admin.add_view(AuthenticatedView(Language, db.session))


@app.route('/ops/login', methods=['POST', 'GET'])
def ops_login():
    if request.method != 'POST':
        return render_template("ops/login.html")

    operator = None
        
    form = OperatorLoginForm(request.form)

    try:
        operator = form.validate_login()
    except:
        flash("Bad login")
        return redirect('/ops/login')

    if operator:
        # login and validate the user...
        session[OPERATOR_ID] = operator.id
        flash("Logged in successfully.")
        app.logger.info("Logged in successfully.")
        return redirect(request.args.get("next") or '/ops')

    return render_template("ops/login.html", form=form)


def operator_login_required(func):
    """
    Decorator to redirect the operator to '/ops/login' if they are not logged in
    """
    @wraps(func)
    def f(*args, **kwargs):
        if not current_operator().is_authenticated():
            app.logger.info('redirecting not logged in operator')
            return redirect(url_for('ops_login'))
        else:
            return func(*args, **kwargs)
    return f


@app.route("/ops/logout")
@operator_login_required
def ops_logout():
    session.clear()
    return redirect('/ops/login')