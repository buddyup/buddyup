from buddyup import app
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crn = db.Column(db.Integer)
    name = db.Column(db.String)


class GroupMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Indicate foreign keys
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    gid = db.Column(db.Integer, db.ForeignKey('group.id'))


class CourseMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    cid = db.Column(db.Integer, db.ForeignKey('course.id'))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: What to use for string size?
    name = db.Column(db.UnicodeText)
    # TODO: Course relationship
    course = db.relationship()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.UnicodeText)
    # TODO: 
    groups = db.relationship('GroupMembership', secondary=


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: How to make this optional?
    gid = db.Column(db.Integer, db.ForeignKey('group.id'))
    time = db.Column(db.DateTime)


class EventMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Indicate foreign keys
    eid = db.Column(db.Integer, db.ForeignKey('event.id'))
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
