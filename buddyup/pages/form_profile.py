#from flask.ext

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed

from wtforms.validators import required, Email, Optional
from wtforms.fields import TextField, RadioField, FieldList, TextAreaField
from wtforms.ext.sqlalchemy.fields import (QuerySelectMultipleField,
                                           QuerySelectField)
from buddyup.app import app
from buddyup.database import Course, Major, Location, db
from buddyup.util import sorted_languages, login_required

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
    full_name = TextField(u'Full Name (required)', validators=[required()])
    COURSE_FORMAT = u"{0.name} by {0.instructor}"
    courses = QuerySelectMultipleField(u"Course(s)",
                                       get_label=COURSE_FORMAT.format,
                                       query_factory=ordered_factory(Course))
    majors = QuerySelectMultipleField(u"Major(s)",
                                      get_label=u"name",
                                      query_factory=ordered_factory(Major))
    languages = QuerySelectMultipleField(u"Other Language(s)",
                                         get_label=u"name",
                                         query_factory=sorted_languages)
    location = QuerySelectField(u"Location",
                                get_label=u"name"
,                                allow_blank=True,
                                query_factory=ordered_factory(Location))
    validators = [FileAllowed(PHOTO_EXTS, u"Images only!")]
    if app.config.get("BUDDYUP_REQUIRE_PHOTO", True):
        validators.append(required())

    photo = FileField(u"Profile Photo (required)", validators=validators)
    facebook = TextField(u"Facebook (optional)")
    twitter = TextField(u"Twitter")
    linkedin = TextField(u"LinkedIn")
    email = TextField(u"Email Address (optional)", validators=[Optional(), Email()])
    bio = TextAreaField(u'A Few Words About You')


class ProfileCreateForm(ProfileForm):
    validators = [FileAllowed(PHOTO_EXTS, u"Images only!")]
    if app.config.get("BUDDYUP_REQUIRE_PHOTO", True):
        validators.append(required())

    photo = FileField(u"Profile Photo (required)", validators=validators)
 

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


# Tutor forms are currently unused


class TutorProfileForm(Form):
    """
    Base class for the create and edit profile forms
    """
    #full_name = TextField(u'Full Name (required)', validators=[required()])
    subjects = QuerySelectMultipleField(u"Subject(s) Tutoring",
                                      get_label=u"name",
                                      query_factory=ordered_factory(Major))
    languages = QuerySelectMultipleField(u"Other Language(s)",
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


