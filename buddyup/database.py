from buddyup.app import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


# n to n relationship tables

CourseMembership = db.Table('coursemembership',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    )


EventMembership = db.Table('eventmembership',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    )


Buddy = db.Table('buddy',
    db.Column('user1_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user2_id', db.Integer, db.ForeignKey('user.id')),
    )


# Main tables


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(3))
    full = db.Column(db.UnicodeText)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crn = db.Column(db.Integer)
    name = db.Column(db.UnicodeText)
    subject = db.Column(db.Integer, db.ForeignKey('subject.id'))
    number = db.Column(db.Integer)
    students = db.relationship('User',
        secondary=CourseMembership,
        backref=db.backref('courses', lazy='dynamic'))
    # TODO
    #events = 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # PSU user names are always <= 8 ASCII characters
    user_name = db.Column(db.String(8))
    full_name = db.Column(db.UnicodeText)
    courses = db.relationship('Course', secondary=CourseMembership,
                              lazy='dynamic')
    events = db.relationship('Event', secondary=EventMembership,
                             lazy='dynamic')
    sent_messages = db.relationship('Message', backref='sender',
                                    lazy='dynamic')
    received_messages = db.relationship('Message', backref='receiver',
                                        lazy='dynamic')
    # TODO
    buddies = db.relationship('User', secondary=Buddy, lazy='dynamic')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    location = db.Column(db.UnicodeText)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    users = db.relationship('User',
        secondary=EventMembership,
        backref=db.backref('events'), lazy='dynamic')
    # TODO
    comments = db.relationship('EventComment', backref='event',
                               lazy='dynamic')


class EventComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contents = db.Column(db.UnicodeText)
    #TODO: submission time
    time = db.Column(db.DateTime)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.UnicodeText)
    #TODO: sending time
    time = db.Column(db.DateTime)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    title = db.Column(db.UnicodeText)
    text = db.Column(db.UnicodeText)
    #TODO: submission time
    time = db.Column(db.DateTime)

class NotesComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes_id = db.Column(db.Integer, db.ForeignKey('notes.id'))
    text = db.Column(db.UnicodeText)
    #TODO: submission time
    time = db.Column(db.DateTime)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.UnicodeText)
    rejected = db.Column(db.Boolean, default=False)
    #Question: just removed it from the db if rejected?
