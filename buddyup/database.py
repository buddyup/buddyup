from buddyup import app
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crn = db.Column(db.Integer)
    name = db.Column(db.UnicodeText)
    subject = db.Column(db.Text)
    number = db.Column(db.Integer)


class CourseMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    cid = db.Column(db.Integer, db.ForeignKey('course.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.UnicodeText)
    # TODO: 
    events = db.relationship('GroupMembership')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship('EventMembership')
    # TODO: Course relationship
    course = db.relationship()
    time = db.Column(db.DateTime)


class EventMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Indicate foreign keys
    eid = db.Column(db.Integer, db.ForeignKey('event.id'))
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
