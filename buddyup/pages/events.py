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
from wtforms import StringField, HiddenField, TextAreaField, SelectField, DateTimeField, IntegerField, TextField, BooleanField
from wtforms.validators import DataRequired, NumberRange, AnyOf
from wtforms.validators import required


SECONDS_IN_A_DAY = 86400
START_OF_DAY = 0
END_OF_DAY = (SECONDS_IN_A_DAY - 1)

TIME_8_00_AM = 28800
TIME_8_30_AM = 30600

class EventForm(Form):
    title = StringField(u'Event Title', validators=[DataRequired()])
    location = StringField(u'Location', validators=[DataRequired()])
    note = TextAreaField(u'Note', default="Here are some additional details...")
    date = DateTimeField(u'Date', format='%m/%d/%y')
    start = SelectField(u'Start', choices = time_pulldown(), coerce=int, validators=[NumberRange(min=START_OF_DAY, max=END_OF_DAY)], default=TIME_8_00_AM)
    end = SelectField(u'End', choices = time_pulldown(),  coerce=int, validators=[NumberRange(min=START_OF_DAY, max=END_OF_DAY)], default=TIME_8_30_AM)
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
    course = User.query.get_or_404(course_id)
    if request.method != 'POST':
        return render_template('courses/events/new.html',
                                course=Course.query.get_or_404(course_id),
                                coursemates=coursemates_query(course.id),
                                times=time_pulldown(),
                                form=form)

    if form.validate():

        date_seconds = epoch_time(form.date.data)

        event = Event(course_id=course_id, owner_id=g.user.id)
        event.name = form.title.data
        event.location = form.location.data
        event.start = datetime.utcfromtimestamp(date_seconds + form.start.data)
        event.end = datetime.utcfromtimestamp(date_seconds + form.end.data)

        event.note = form.note.data

        db.session.add(event)

        # The event owner should automatically join the new event.
        g.user.events.append(event)

        db.session.commit()

        invite_everyone = (request.form.get("everyone") == "true")
        invited = [int(id) for id in request.form.getlist("invited")]

        invitees = coursemates_query(course.id)

        # TODO: Need to prevent people already invited from being reinvited.
        if not invite_everyone:
            invitees = coursemates_query(course.id).filter(User.id.in_(invited))

        for invitee in invitees:
            send_event_invitation(g.user, invitee, event)

        flash("Invitations sent.")

        return redirect(url_for('course_event', course_id=course.id, event_id=event.id))
    else:
        field_names = form.errors.keys()
        flash("There was a problem. Please look over the information you've given and make sure it is correct.")
        coursemates = coursemates_query(course.id)
        return render_template('courses/events/new.html',
                                course=Course.query.get_or_404(course_id),
                                coursemates=coursemates,
                                times=time_pulldown(),
                                form=form)


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
    # attendees = db.session.query(EventMembership).join(Event).filter(Event.id==event.id).all()
    attendees = User.query.join(EventMembership).join(Event).filter(EventMembership.c.event_id==event.id).all()

    return render_template('courses/events/view.html',
                            course=course,
                            event=event,
                            comments=comments,
                            join_form=EventRSVPForm(),
                            invite_form=EventInvitationForm(),
                            comment_form=EventCommentForm(),
                            coursemates=coursemates_query(course.id),
                            attending=attending,
                            attendees=attendees)


class EventInvitationForm(Form):
    # We're only using the form for its CSRF token.
    pass

class EventCommentForm(Form):
    contents = TextField(validators=[required()])


class EventRSVPForm(Form):
    attending = TextField(validators=[required(), AnyOf(["true", "false"])])
    @property
    def is_attending(self):
        return self.attending.data == "true"

from buddyup.util import send_notification

def send_event_invitation(sender, receiver, event):
    invitation = EventInvitation()
    invitation.event_id = event.id
    invitation.sender_id = g.user.id
    invitation.receiver_id = receiver.id
    db.session.add(invitation)
    db.session.commit()

    event_link = '<a href="%s">%s</a>' % (url_for('course_event', course_id=event.course.id, event_id=event.id), event.name)

    payload = "%s invited you to '%s'" % (sender.full_name, event_link)
    text = "Accept"
    link = url_for('accept_event_invitation', course_id=event.course.id, event_id=event.id, invitation_id=invitation.id)

    send_notification(sender, receiver, payload, action_text=text, action_link=link)




from buddyup.pages.courses import coursemates_query
@app.route('/courses/<int:course_id>/events/<int:event_id>/invitation', methods=['GET', 'POST'])
@login_required
def course_event_invitation(course_id, event_id):
    form = EventInvitationForm()
    course = Course.query.get_or_404(course_id)
    event = Event.query.get_or_404(event_id)

    if form.validate_on_submit():
        invite_everyone = (request.form.get("everyone") == "true")
        invited = [int(id) for id in request.form.getlist("invited")]

        invitees = coursemates_query(course.id)

        if not invite_everyone:
            already_invited = [i.receiver_id for i in EventInvitation.query.filter(EventInvitation.event_id==event_id)]

            # Invite selected coursemates as long as they aren't already invited by the current user.
            invitees = coursemates_query(course.id)\
                                        .filter(User.id.in_(invited))\
                                        .filter(~User.id.in_(already_invited))

        for invitee in invitees:
            send_event_invitation(g.user, invitee, event)

        if invitees.count() > 0:
            flash("Invitations sent.")

        return redirect(url_for('course_event', course_id=course.id, event_id=event.id))
    else:
        coursemates = coursemates_query(course.id)
        return render_template('courses/events/invite.html', form=form, course=course, event=event, coursemates=coursemates)


def clear_event_invites(user_id, event_id):
    EventInvitation.query.filter(EventInvitation.event_id==event_id, EventInvitation.receiver_id==user_id).delete()
    db.session.commit()


@app.route('/courses/<int:course_id>/events/<int:event_id>/invitations/<int:invitation_id>', methods=['POST'])
@login_required
def accept_event_invitation(course_id, event_id, invitation_id):

    invitation = EventInvitation.query.get_or_404(invitation_id)

    # If we're not the receiver we see nothing.
    if invitation.receiver != g.user: abort(404)

    # Join the event.
    g.user.events.append(invitation.event)

    clear_event_invites(g.user.id, invitation.event.id)

    return "{}"



@app.route('/courses/<int:course_id>/events/<int:event_id>/attendee', methods=['GET', 'POST'])
@login_required
def course_event_attend(course_id, event_id):
    rsvp = EventRSVPForm()
    event = Event.query.get_or_404(event_id)

    if rsvp.validate_on_submit():
        if rsvp.is_attending:
            g.user.events.append(event)
            db.session.commit()
        else:
            g.user.events.remove(event)
            db.session.commit()

        clear_event_invites(g.user.id, event.id)

        return "{}"
    else:
        return rsvp.csrf_token.current_token



@app.route('/courses/<int:course_id>/events/<int:event_id>/comment', methods=['GET', 'POST'])
@login_required
def course_event_comment(course_id, event_id):

    form = EventCommentForm()
    course = Course.query.get_or_404(course_id)
    event = Event.query.get_or_404(event_id)

    if form.validate_on_submit():
        comment = EventComment()
        comment.event_id = event_id
        comment.user_id = g.user.id
        comment.contents = form.contents.data
        comment.time = datetime.now()

        db.session.add(comment)
        db.session.commit()

    # No matter what, come back to the event page.
    return redirect(url_for('course_event', course_id=course_id, event_id=event_id))


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







