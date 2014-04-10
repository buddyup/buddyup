from buddyup.app import app
from buddyup.database import (Course, Visit, User, BuddyInvitation,
                              Location, Major, Event, Language, CourseMembership,
                              db)
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView


admin = Admin(app, url="/ops", name="BuddyUp Operations")

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(BuddyInvitation, db.session, "Invitation"))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Major, db.session))
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Language, db.session))
