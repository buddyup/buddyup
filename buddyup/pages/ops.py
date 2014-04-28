from buddyup.app import app
from buddyup.database import (Course, Visit, User, BuddyInvitation,
                              Location, Major, Event, Language, CourseMembership,
                              Operator,
                              db)
from flask import Flask, redirect, request, render_template, flash
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from wtforms import form, fields, validators


from flask.ext.login import LoginManager, login_required, login_user, logout_user
 
login_manager = LoginManager()
login_manager.init_app(app)


import hashlib
# Define login and registration forms (for flask-login)
class OperatorLoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid login')

        if hashlib.sha256(self.password.data).hexdigest() != user.password:
            raise validators.ValidationError('Invalid password')
        
        return user

    def get_user(self):
        print "Operator: %s" % db.session.query(Operator).first()
        print "Login given: %s" % self.login.data
        return db.session.query(Operator).filter_by(login=self.login.data).first()

    def __repr__(self):
        return '%s' % self.login



@login_manager.user_loader
def load_operator(id):
    return Operator.get(id)
    
class AuthenticatedView(ModelView):
    def is_accessible(self):
        return False

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
        
    form = OperatorLoginForm(request.form)
    print "form: %s" % form
    operator = form.validate_login()
    if operator:
        # login and validate the user...
        login_user(operator)
        flash("Logged in successfully.")
        app.logger.info("Logged in successfully.")
        return redirect(request.args.get("next") or '/ops')
    return render_template("ops/login.html", form=form)
    #return redirect('/ops')


@app.route("/ops/logout")
@login_required
def ops_logout():
    logout_user()
    return redirect('/ops')