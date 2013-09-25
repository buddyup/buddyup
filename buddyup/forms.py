from flask import g, abort

from flask.ext.wtf import Form
from wtforms import TextField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from buddyup.database import Course, Location, Major


def course_required(form, field):
    try:
        course_id = int(field.data)
    except ValueError:
        abort(400)
    if g.user.courses.filter(Course.id == course_id).count() == 0:
        abort(403)


def query_user_courses():
    return g.user.courses.all()


class QuestionForm(Form):
    course = QuerySelectField(query_factory=query_user_courses,
                              get_label="name")
    title = TextField(u'Title', validators=[DataRequired()])
    text = TextAreaField(u'Question')


class AnswerForm(Form):
    question_id = HiddenField()
    text = TextAreaField(u"Answer", validators=[DataRequired()])
