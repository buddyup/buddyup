import datetime

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

MajorMembership = db.Table('majormembership',
    db.Column('major_id', db.Integer, db.ForeignKey('major.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    )

Buddy = db.Table('buddy',
    db.Column('user1_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user2_id', db.Integer, db.ForeignKey('user.id')),
    )


LanguageMembership = db.Table('languagemembership',
    db.Column('language_id', db.Integer, db.ForeignKey('language.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    )



# Main tables

class EventInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class BuddyInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.UnicodeText)
    rejected = db.Column(db.Boolean, default=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText)
    instructor = db.Column(db.UnicodeText)
    events = db.relationship('Event', backref='course')

    def __repr__(self):
        return self.name
 
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payload = db.Column(db.UnicodeText, default=u"")
    action_text = db.Column(db.UnicodeText, default=u"")
    action_link = db.Column(db.UnicodeText, default=u"")
    deleted = db.Column(db.Boolean, default=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Note: Portland State University user names are always <= 8 ASCII characters
    user_name = db.Column(db.String(255), index=True, unique=True)
    full_name = db.Column(db.UnicodeText, default=u"")
    bio = db.Column(db.UnicodeText, default=u"")
    facebook = db.Column(db.UnicodeText, default=u"")
    facebook_token = db.Column(db.UnicodeText)
    twitter = db.Column(db.UnicodeText, default=u"")
    twitter_token = db.Column(db.UnicodeText)
    twitter_secret = db.Column(db.UnicodeText)
    linkedin = db.Column(db.UnicodeText, default=u"")
    linkedin_token = db.Column(db.UnicodeText)
    google_token = db.Column(db.UnicodeText)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    email = db.Column(db.UnicodeText)
    has_photos = db.Column(db.Boolean, default=False)
    #tutor = db.Column(db.Boolean, default = False)

    # Initialized flag
    initialized = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '%s' % self.full_name

    # Relationships
    location = db.relationship('Location')
    courses = db.relationship('Course',
                              secondary=CourseMembership,
                              backref=db.backref('users', lazy="dynamic"),
                              lazy='dynamic')
    majors = db.relationship('Major', lazy="dynamic",
                             secondary=MajorMembership,
                             backref='users')
    languages = db.relationship('Language', lazy='dynamic',
                                secondary=LanguageMembership,
                                backref=db.backref('users', lazy="dynamic"))
    notifications = db.relationship('Notification', backref='recipient',
                                primaryjoin=Notification.recipient_id == id)

    notifications_sent = db.relationship('Notification', backref='sender',
                                primaryjoin=Notification.sender_id == id)

    buddies = db.relationship('User', secondary=Buddy,
                              lazy='dynamic',
                              primaryjoin=Buddy.c.user1_id == id,
                              secondaryjoin=Buddy.c.user2_id == id)
    buddy_invitations_sent = db.relationship('BuddyInvitation', backref='sender',
                                primaryjoin=BuddyInvitation.sender_id == id)
    buddy_invitations_received = db.relationship('BuddyInvitation', backref='receiver',
                                primaryjoin=BuddyInvitation.receiver_id==id)

    events = db.relationship('Event', lazy="dynamic",
                             secondary=EventMembership,
                             backref=db.backref('users', lazy="dynamic"))
    event_invitations_sent = db.relationship('EventInvitation', backref='sender',
                                primaryjoin=EventInvitation.sender_id==id)
    event_invitations_received = db.relationship('EventInvitation', backref='receiver',
                                primaryjoin=EventInvitation.receiver_id==id,
                                lazy="dynamic")


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.UnicodeText, default=u"")
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    # TODO: Amazon S3 bucket and friends

    def __repr__(self):
        return '<Photo %r>' % self.id


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship("User")
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    name = db.Column(db.UnicodeText)
    location = db.Column(db.UnicodeText)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    note = db.Column(db.UnicodeText)
    invitation = db.relationship('EventInvitation', backref='event')

    def __repr__(self):
        return '<Event %r>' % self.id

class EventComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship("Event")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")
    contents = db.Column(db.UnicodeText)
    #TODO: submission time
    time = db.Column(db.DateTime)

    def __repr__(self):
        return '<EventComment %r>' % self.id


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime)
    read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Message> %r>' % self.id

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    title = db.Column(db.UnicodeText)
    text = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<Notes %r>' % self.id


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    requests = db.Column(db.Integer, default=1)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True)

    def __repr__(self):
        return '%s' % self.name


class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True)

    def __repr__(self):
        return self.name


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True)

    def __repr__(self):
        return '%s' % self.name


class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.String(64))

    def __repr__(self):
        return u'%s' % self.login

    authenticated = False

    def is_authenticated(self):
        return self.authenticated


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(255))
    verb = db.Column(db.String(8))

class TutorApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
