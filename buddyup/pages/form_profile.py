#from flask.ext
import re

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed

from wtforms.validators import required, Email, Optional, Regexp, ValidationError
from wtforms.fields import TextField, RadioField, FieldList, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import (QuerySelectMultipleField,
                                           QuerySelectField)
from buddyup.app import app, in_production
from buddyup.database import Course, Major, Location, db
from buddyup.util import sorted_languages, login_required, QueryMultiCheckboxField, QueryRadioField


PHOTO_EXTS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff']
# Python 3: infinite loop because map() is lazy, use list(map(...))
# The next version of Flask-WTF will have a fix to be case-insensitive.
PHOTO_EXTS.extend(map(str.upper, PHOTO_EXTS))

def ordered_factory(record_type, field="name"):
    def factory():
        return record_type.query.order_by(field)
    return factory


class ProfileForm(Form):
    """
    Base class for the create and edit forms
    """
    full_name = TextField(u'Full Name', validators=[required()])
    COURSE_FORMAT = u"{0.name}"
    courses = QueryMultiCheckboxField(u"Course(s)",
                                       get_label=COURSE_FORMAT.format,
                                       query_factory=ordered_factory(Course))
    majors = QuerySelectMultipleField(u"Major(s)",
                                      get_label=u"name",
                                      query_factory=ordered_factory(Major))
    languages = QueryMultiCheckboxField(u"Other Language(s)",
                                         get_label=u"name",
                                         query_factory=sorted_languages)
    location = QueryRadioField(u"Where do you live?",
                                get_label=u"name",
                                allow_blank=True,
                                blank_text="None of these",
                                query_factory=ordered_factory(Location))
    validators = [FileAllowed(PHOTO_EXTS, u"Images only!")]
    if app.config.get("BUDDYUP_REQUIRE_PHOTO", True) and in_production():
        validators.append(required())

    photo = FileField(u"Profile Photo", validators=validators)
    facebook = TextField(u"Facebook (optional)")
    twitter = TextField(u"Twitter")
    linkedin = TextField(u"LinkedIn")
    email = TextField(u".edu Email Address", validators=[required(), Email(), Regexp("^([^@?]*)@([A-z_\.]*)(buddyup\.org|\.edu\.au|\.edu\.jp|\.edu)$", flags=re.IGNORECASE, message=u'You must use your .edu email address.')])
    bio = TextAreaField(u'A Few Words About You')


def not_existing_course(form, field):
    matches = Course.query.filter(Course.name==field.data.upper())
    if matches.count() > 0:
        raise ValidationError('Course already exists!')

class CourseCreationForm(Form):
    name = TextField(u'Full Name', validators=[required(), not_existing_course])

class ProfileCreateForm(ProfileForm):
    validators = [FileAllowed(PHOTO_EXTS, u"Images only!")]
    if app.config.get("BUDDYUP_REQUIRE_PHOTO", True) and in_production():
        validators.append(required())

    photo = FileField(u"Profile Photo", validators=validators)
 

class ProfileUpdateForm(ProfileForm):
    """
    Base class for the create and edit profile forms
    """
    photo = FileField(u"Profile Photo (optional)", validators=[
                      FileAllowed(PHOTO_EXTS, u"Images only!")])


class PhotoCreateForm(Form):
    photo = FileField(u"Profile Photo", validators=[required(),
                      FileAllowed(PHOTO_EXTS, u"Images only!")])


class PhotoDeleteForm(Form):
    """
    Empty form to get crsf token support
    """




class TutorApplicationForm(Form):
    """
    Base class for the create and edit profile forms
    """
    courses = QueryMultiCheckboxField(u"Courses",
                                      get_label=u"name",
                                      query_factory=ordered_factory(Course))
    languages = QueryMultiCheckboxField(u"Languages",
                                         get_label=u"name",
                                         query_factory=sorted_languages)

    # status = SelectField("Status", choices=[("looking", "Looking for new clients"), ("interested", "Interested in becoming a tutor")])

    location = QueryRadioField(u"Location",
                                get_label=u"name",
                                allow_blank=True,
                                query_factory=ordered_factory(Location))

    # TODO: decide on this, long-term
    # price = TextField(u"Price", validators=[Optional()])
    # per = SelectField(choices=[("hour", "per hour"), ("session", "per session")])


# Tutor forms below are currently unused

class TutorProfileForm(Form):
    """
    Base class for the create and edit profile forms
    """
    #full_name = TextField(u'Full Name (required)', validators=[required()])
    subjects = QueryMultiCheckboxField(u"Subject(s) Tutoring",
                                      get_label=u"name",
                                      query_factory=ordered_factory(Major))
    languages = QueryMultiCheckboxField(u"Other Language(s)",
                                         get_label=u"name",
                                         query_factory=sorted_languages)
    #location = QuerySelectField(u"Location",
                                #get_label=u"name",
                                #allow_blank=True,
                                #query_factory=ordered_factory(Location))
    #photo = FileField(u"Profile Photo (required)", validators=[
                      #required(),
                      #FileAllowed(PHOTO_EXTS, u"Images only!")])
    #facebook = TextField(u"Facebook")
    #twitter = TextField(u"Twitter")
    #linkedin = TextField(u"LinkedIn")
    email = TextField(u"Email Address", validators=[Optional(), Email()])
    bio = TextAreaField(u'A Few Words About You (required)', validators=[required()])


class TutorProfileCreateForm(TutorProfileForm):
    pass


class TutorProfileUpdateForm(TutorProfileForm):
    """
    Base class for the create and edit profile forms
    """
    #photo = FileField(u"Profile Photo (optional)", validators=[
                      #Optional(),
                      #FileAllowed(PHOTO_EXTS, u"Images only!")])


