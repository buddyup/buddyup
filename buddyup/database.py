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

#TutorSubject = db.Table('tutorsubject',
#    db.Column('major_id', db.Integer, db.ForeignKey('major.id')),
#    db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id')),
#    )

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

#TutorLanguage = db.Table('tutorlanguage',
#    db.Column('language_id', db.Integer, db.ForeignKey('language.id')),
#    db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id')))


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
    #Question: just removed it from the db if rejected?


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText)
    instructor = db.Column(db.UnicodeText)
    events = db.relationship('Event', backref='course')
    questions = db.relationship('Question', backref='course', lazy='dynamic')

    def __repr__(self):
        return self.name


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    title = db.Column(db.UnicodeText)
    text = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime)
    votes = db.relationship("AnswerVote", backref="answer", lazy='dynamic')
    
    @property
    def html_id(self):
        return 'a%d' % self.id
 

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    title = db.Column(db.UnicodeText)
    text = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime)
    #TODO: Add a counter of views?
    answers = db.relationship("Answer",
            backref="Question", lazy='dynamic',
            primaryjoin=Answer.question_id == id)
    votes = db.relationship("QuestionVote", backref="question",
                            lazy='dynamic')

    def __repr__(self):
        return '<Question %r>' % self.id
 
    @property
    def html_id(self):
        return 'q%d' % self.id


class AnswerVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    # May change value into boolean
    value = db.Column(db.Integer)


class QuestionVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    # May change value into boolean
    value = db.Column(db.Integer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # PSU user names are always <= 8 ASCII characters due to Solaris
    # restrictions
    user_name = db.Column(db.String(32), index=True, unique=True)
    full_name = db.Column(db.UnicodeText, default=u"")
    bio = db.Column(db.UnicodeText, default=u"")
    facebook = db.Column(db.UnicodeText, default=u"")
    twitter = db.Column(db.UnicodeText, default=u"")
    linkedin = db.Column(db.UnicodeText, default=u"")
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    email = db.Column(db.UnicodeText)
    has_photos = db.Column(db.Boolean, default=False)
    #tutor = db.Column(db.Boolean, default = False)

    # Initialized flag
    initialized = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '%s' % self.full_name

    # Photos
   
    # Relationships
    location = db.relationship('Location')
    courses = db.relationship('Course',
                              secondary=CourseMembership,
                              backref=db.backref('users', lazy="dynamic"),
                              lazy='dynamic')
    events = db.relationship('Event', lazy="dynamic",
                             secondary=EventMembership,
                             backref=db.backref('users', lazy="dynamic"))
    buddies = db.relationship('User', secondary=Buddy,
                              lazy='dynamic',
                              primaryjoin=Buddy.c.user1_id == id,
                              secondaryjoin=Buddy.c.user2_id == id)
    sent_bud_inv = db.relationship('BuddyInvitation', backref='sender',
                                primaryjoin=BuddyInvitation.sender_id == id)
    received_bud_inv = db.relationship('BuddyInvitation', backref='receiver',
                                primaryjoin=BuddyInvitation.receiver_id==id)
    sent_eve_inv = db.relationship('EventInvitation', backref='sender',
                                primaryjoin=EventInvitation.sender_id==id)
    received_event_inv = db.relationship('EventInvitation', backref='receiver',
                                primaryjoin=EventInvitation.receiver_id==id,
                                lazy="dynamic")
    majors = db.relationship('Major', lazy="dynamic",
                             secondary=MajorMembership,
                             backref='users')
    languages = db.relationship('Language', lazy='dynamic',
                                secondary=LanguageMembership,
                                backref=db.backref('users', lazy="dynamic"))
    questions = db.relationship('Question', lazy="dynamic", backref='user',
                                primaryjoin=Question.user_id == id)
    answers = db.relationship('Answer', lazy="dynamic", backref='user',
                              primaryjoin=Answer.user_id == id)
    available = db.relationship('Availability', lazy="dynamic",
                                backref="user")
#    buddy_inv = db.relationship('User', secondary=BuddyInvitation,
#                                primaryjoin=BuddyInvitation.c.receiver_id == id,
#                                secondaryjoin=BuddyInvitation.c.sender_id == id)
#    group_inv = db.relationship('User', secondary=EventInvitation,
#                                primaryjoin=EventInvitation.c.event_id == id,
#                                secondaryjoin=EventInvitation.c.user_id == id)


#class Tutor(db.Model):    
#	id = db.Column(db.Integer, primary_key=True)
#    user_name = db.Column(db.String(8), index=True, unique=True)   
    # Photos
   
    # Relationships
#    subject_tutoring = db.relationship('Major', secondary = TutorSubject,
#                                backref=db.backref('tutors', lazy="dynamic"),
#                                lazy='dynamic')
#    languages = db.relationship('Language', lazy = 'dynamic',
#                            secondary = TutorLanguage,
#                            backref = db.backref('tutors', lazy='dynamic'))
#    available = db.relationship('AvailabilityTutor', lazy = "dynamic", backref = "tutors")
#    bio = db.Column(db.UnicodeText, default=u"")

    

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
    # TODO: this users relationship may be wrong
    #users = db.relationship('User', secondary=EventMembership,
    #                        lazy='dynamic')
        #backref=db.backref('events'), lazy='dynamic')
    # TODO
#    comments = db.relationship('EventComment', backref='event',
#                               lazy='dynamic')

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
    # I don't think Notes need time - Will
    # time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Notes %r>' % self.id

'''class NotesComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes_id = db.Column(db.Integer, db.ForeignKey('notes.id'))
    text = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime)

    def __init__(self, notes_id, text, time):
        self.notes_id = notes_id
        self.text = text
        self.time = time

    def __repr__(self):
        return '<NotesComment %r>' % self.id
'''

   


class Availability(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
            primary_key=True)
    day = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Enum('am', 'pm', name="ampm"), primary_key=True)


#class AvailabilityTutor(db.Model):
#    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), primary_key = True)
#    day = db.Column(db.Integer, primary_key = True)
#    time = db.Column(db.Enum('am', 'pm', name="ampm"), primary_key = True)


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
    password = db.Column(db.String(32))

    def __repr__(self):
        return u'%s' % self.login

    authenticated = False

    def is_authenticated(self):
        return self.authenticated