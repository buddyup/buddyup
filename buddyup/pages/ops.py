from buddyup.app import app
from buddyup.database import (Course, Visit, User, BuddyInvitation,
                              Location, Major, Event, Language, CourseMembership,
                              db)
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

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
