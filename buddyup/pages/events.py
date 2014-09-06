from flask import (g, request, flash, redirect, url_for, session, abort,
                   get_flashed_messages, jsonify)
from datetime import datetime, timedelta
import time
from functools import partial
import re

from buddyup.app import app
from buddyup.database import Event, Course, EventInvitation, db, EventComment
from buddyup.templating import render_template
from buddyup.util import (args_get, login_required, form_get, check_empty,checked_regexp, calendar_event, easy_datetime, time_pulldown, epoch_time)

import os


#--------------------- NEW STUFF BELOW ---------------------------

from flask.ext.wtf import Form
from wtforms import StringField, HiddenField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, NumberRange


SECONDS_IN_A_DAY = 86400
START_OF_DAY = 0
END_OF_DAY = (SECONDS_IN_A_DAY - 1)


class EventForm(Form):
    title = StringField(u'Event Title', validators=[DataRequired()])
    location = StringField(u'Location', validators=[DataRequired()])
    note = TextAreaField(u'Note')
    date = DateTimeField(u'Date', format='%m/%d/%y')
    start = SelectField(u'Start', choices = time_pulldown(), coerce=int, validators=[NumberRange(min=START_OF_DAY, max=END_OF_DAY)])
    end = SelectField(u'End', choices = time_pulldown(),  coerce=int, validators=[NumberRange(min=START_OF_DAY, max=END_OF_DAY)])


@app.route('/courses/<int:course_id>/event', methods=['GET', 'POST'])
@login_required
def new_event(course_id):
    form = EventForm()
    if request.method != 'POST': return render_template('courses/new-event.html', course=Course.query.get_or_404(course_id), times=time_pulldown(), form=form)

    if form.validate():

        date_seconds = epoch_time(form.date.data)

        event = Event(course_id=course_id, owner_id=g.user.id)
        event.name = form.title.data
        event.location = form.location.data
        event.start = datetime.utcfromtimestamp(date_seconds + form.start.data)
        event.end = datetime.utcfromtimestamp(date_seconds + form.end.data)

        db.session.add(event)
        db.session.commit()


        flash('"%s" was added to the %s calendar for %s.' % (form.title.data, Course.query.get(course_id).name, datetime.strftime(event.start, "%m/%d at %H:%M %p")))
        return redirect(url_for('course_events', id=course_id))
    else:
        field_names = form.errors.keys()
        flash("Missing important information: %s. Try again." % ", ".join(["%s" % name.capitalize() for name in field_names]))
        return render_template('courses/new-event.html', course=Course.query.get_or_404(course_id), times=time_pulldown(), form=form)


@app.route('/courses/<int:id>/events.json')
@login_required
def course_events_json(id):
    course = Course.query.get_or_404(id)

    data = {}
    data["success"] = 1
    data["result"] = [calendar_event(event) for event in course.events]

    return jsonify(data)

@app.route('/courses/<int:id>/events')
@login_required
def course_events(id):
    course = Course.query.get_or_404(id)
    events = Event.query.filter(Course.id==course.id).order_by(Event.start)
    return render_template('courses/events.html', course=course, events=events)


@app.route('/courses/<int:course_id>/events/<int:event_id>')
@login_required
def course_event(course_id, event_id):
    course = Course.query.get_or_404(course_id)
    event = Event.query.get_or_404(event_id)
    comments = EventComment.query.filter(EventComment.event_id == Event.id, Event.id == event.id)
    return render_template('courses/event-detail.html', course=course, event=event, comments=comments)


@app.route('/events')
@login_required
def my_events():
    return render_template('my_events.html', all_events="selected", events=g.user.events.order_by(Event.start))


# TODO: Move these helpers into some sort of view/adapter class
@app.template_global()
@app.template_filter()
def date_short(event):
    return event.start.strftime("%b %d") if event else ""

@app.template_global()
@app.template_filter()
def date_long(event):
    return event.start.strftime("%b %d, %Y") if event else ""


@app.template_global()
@app.template_filter()
def time_span(event):
    return "%s-%s" % (event.start.strftime("%I%p").lstrip("0"), event.end.strftime("%I%p").lstrip("0"))







