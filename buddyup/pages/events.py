from flask import (g, request, flash, redirect, url_for, session, abort,
                   get_flashed_messages, jsonify)
from datetime import datetime, timedelta
import time
from functools import partial
import re

from buddyup.app import app
from buddyup.database import Event, Course, EventInvitation, db, EventComment, User, EventMembership
from buddyup.templating import render_template
from buddyup.util import (args_get, login_required, form_get, check_empty,checked_regexp, calendar_event, easy_datetime, time_pulldown, epoch_time)

import os


#--------------------- NEW STUFF BELOW ---------------------------

from flask.ext.wtf import Form
from wtforms import StringField, HiddenField, TextAreaField, SelectField, DateTimeField, IntegerField, TextField
from wtforms.validators import DataRequired, NumberRange, AnyOf
from wtforms.validators import required


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
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        else:
            if self.start.data > self.end.data:
                self.start.errors.append('Start time must be before end time.')
                return False
        return True


@app.route('/courses/<int:course_id>/event', methods=['GET', 'POST'])
@login_required
def new_event(course_id):
    form = EventForm()
    if request.method != 'POST': return render_template('courses/events/new.html', course=Course.query.get_or_404(course_id), times=time_pulldown(), form=form)

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
        flash("There was a problem. Please look over the information you've given and make sure it is correct.")
        return render_template('courses/events/new.html', course=Course.query.get_or_404(course_id), times=time_pulldown(), form=form)


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
    events = Event.query.join(Course).filter(Course.id==course.id).order_by(Event.start)
    return render_template('courses/events/events.html', course=course, events=events)


@app.route('/courses/<int:course_id>/events/<int:event_id>')
@login_required
def course_event(course_id, event_id):
    course = Course.query.get_or_404(course_id)
    event = Event.query.get_or_404(event_id)
    comments = EventComment.query.filter(EventComment.event_id == Event.id, Event.id == event.id)
    attending = event in g.user.events
    attendees = db.session.query(EventMembership).join(Event).filter(Event.id==event.id).all()

    return render_template('courses/events/view.html',
                            course=course,
                            event=event,
                            comments=comments,
                            form=EventRSVPForm(),
                            attending=attending,
                            attendees=attendees)


class EventInvitationForm(Form):
    receiver_id = IntegerField(validators=[required()])

class EventRSVPForm(Form):
    attending = TextField(validators=[required(), AnyOf(["true", "false"])])


@app.route('/courses/<int:course_id>/events/<int:event_id>/invitation', methods=['GET', 'POST'])
@login_required
def course_event_invitation(course_id, event_id):
    form = EventInvitationForm()

    if form.validate_on_submit():
        invitation = EventInvitation()
        invitation.event_id = event_id
        invitation.sender_id = g.user.id
        invitation.receiver_id = form.receiver_id.data
        db.session.add(invitation)
        db.session.commit()
        return "{}"
    else:
        return form.csrf_token.current_token


@app.route('/courses/<int:course_id>/events/<int:event_id>/attendee', methods=['GET', 'POST'])
@login_required
def course_event_attend(course_id, event_id):
    form = EventRSVPForm()
    event = Event.query.get_or_404(event_id)

    if form.validate_on_submit():
        if form.attending.data == "true":
            app.logger.info("ATTEND")
            g.user.events.append(event)
            db.session.commit()
        else:
            app.logger.info("BAIL")
            g.user.events.remove(event)
            db.session.commit()

        return "{}"
    else:
        return form.csrf_token.current_token



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







