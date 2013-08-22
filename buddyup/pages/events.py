from flask import (g, request, flash, redirect, url_for, session, abort,
                   get_flashed_messages)
from datetime import datetime, timedelta
import time
from functools import partial
import re

from buddyup.app import app
from buddyup.database import Event, Course, EventInvitation, db, EventComment
from buddyup.templating import render_template
from buddyup.util import (args_get, login_required, form_get, check_empty,
                          events_to_json, checked_regexp)

TIME_REGEXP = re.compile(r"""
    (?P<hour>\d\d?)       # hour
    (:(?P<minute>\d\d))?  # minute (optional)
""", flags=re.VERBOSE)
DATE_REGEXP = re.compile(r"""
    (?P<month>\d{1,2})[-/]  # month
    (?P<day>\d{1,2})[-/]    # day
    (?:20)?                 # optional '20' year prefix
    (?P<year>\d{2})         # year (xx)
""", flags=re.VERBOSE)


def parse_date(date, label):
    match = checked_regexp(DATE_REGEXP, date, label)
    if match:
        year = int(match.group('year')) + 2000
        month = int(match.group('month'))
        day = int(match.group('day'))
        return datetime(year, month, day)
    else:
        return None


def parse_time(time_string, ampm, base, label):
    match = checked_regexp(TIME_REGEXP, time_string, label)
    if match:
        hour = int(match.group('hour'))
        minute = int(match.group('minute') or 0)
        # Convert 12-hour time to 24-hour time
        if ampm == 'am':
            if hour == 12:
                hour = 0
        elif ampm == 'pm':
            hour += 12
        else:
            # Must be AM or PM!
            abort(400)
        return base + timedelta(hours=hour, minutes=minute)
    else:
        return None


@app.route('/event')
@login_required
def event_view_all():
    # TODO: view all events that relates to the currently active user
    events = g.user.events.all()
    return render_template('event_view_all.html', events=events)

@app.route('/event/view/<int:event_id>')
@login_required
def event_view(event_id):
    event_record = Event.query.get_or_404(event_id)
    event_comments = EventComment.query.filter_by(event_id=event_id).order_by(EventComment.time).all()
    is_owner = event_record.owner_id  == g.user.id
    if is_owner:
        in_event = True
    else:
        in_event = event_record.users.filter_by(id=g.user.id).count() == 1
    remove_url = url_for('event_remove', event_id=event_record.id)
    leave_url = url_for('leave_event', event_id=event_record.id)
    join_url = url_for('attend_event', event_id=event_record.id)
    return render_template('group/view.html',
                            event_record=event_record,
                            event_comments=event_comments,
                            is_owner=is_owner,
                            remove_url=remove_url,
                            leave_url=leave_url,
                            join_url=join_url,
                            owner=event_record.owner,
                            in_event=in_event,
                            )


@app.route('/event/search')
@login_required
def event_search():
    return render_template('group/search.html',
                           courses=g.user.courses.all(),
                           selected=lambda _: False)


@app.route('/event/search_results')
@login_required
def event_search_results():
    """
    Gives event_search_results.html a Pagination (see Flask-SQLAlchemy) of
    Events.
    
    Should this be GET?
    """

    get_int = partial(args_get, convert=int)
    # TODO: Addition ordering?
    query = Event.query
    query = query.order_by(Event.start)
    query = query.filter(Event.start > datetime.now())

    course = get_int('course')
    # -1 indicates no course selected, so use all courses
    if course >= 0:
        query = query.filter_by(course_id=course)
    else:
        course_ids = [course.id for course in g.user.courses.all()]
        query = query.filter(Event.course_id.in_(course_ids))
    
    date_text = args_get('date')
    if date_text:
        date = parse_date(date_text, "Date")
        query = query.filter(Event.start > date,
                             Event.start < (date + timedelta(day=1)))
    else:
        query = query.filter(Event.start > datetime.now())
        
    

    #page = args_get('page', convert=int, default=0)
    #if page < 0:
        #page = 0
    #else:
        #page = page - 1
        #query = query.filter(start < Event.start).filter(end > Event.end)
    
    # AM/PM searching is difficult to do cross database, so just filter app
    # app side.
    ampm = args_get('start_time', default='whynotboth')
    if ampm == 'am':
        events = (event for event in query.all()
                  if event.start.hour < 12)
    elif ampm == 'pm':
        events = (event for event in query.all()
                  if event.start.hour >= 12)
    else:  # aka whynotboth
        events = query.all()

    search_results = []
    already_attending = {event.id for event in g.user.events.all()}
    for event in events:
        search_results.append({
            'name': event.name,
            # TODO: strftime
            # Month/Day/Year Hour:Minute
            'timestamp': event.start.strftime("%m/%d/%Y %I:%M %p"),
            'people_count': event.users.count(),
            'view': url_for('event_view', event_id=event.id),
            'attending': event.id in already_attending,
            'attend_link': url_for('attend_event', event_id=event.id),
            'is_owner': event.owner.id == g.user.id,
            'delete_link': url_for('event_remove', event_id=event.id),
            'leave_link': url_for('leave_event', event_id=event.id),
        })
    if get_flashed_messages():
        return redirect(url_for('event_search'))
    else:
        return render_template('group/search_result.html',
                               groups=search_results)
    #return render_template('group/search_results.html',
    #                       pagination=query.pagination())

@app.route('/event/create', methods=['GET','POST'])
@login_required
def event_create():
    if request.method == 'GET':
        # TODO: pass out the user's course to set it as default
        return render_template('group/create.html',
                               courses=g.user.courses.all(),
                               has_errors=False,
                               selected=lambda record: False)
    else:
        user = g.user
        name = form_get('name')
        check_empty(name, "Event Name")
        course_id = form_get('course', convert=int)
        location = form_get('location')
        check_empty(location, "Location")
        note = form_get('note')
        # Date
        date = parse_date(form_get('date'), "Date")

        # Start Time
        start = parse_time(form_get('start'), form_get('start_ampm'),
                           date, "Start")
        end = parse_time(form_get('end'), form_get('end_ampm'),
                         date, "End")
        

        if get_flashed_messages():
            def selected(record):
                assert isinstance(record, Course)
                return record.id == course_id
            return render_template('group/create.html',
                                   courses=g.user.courses.all(),
                                   has_errors=True,
                                   selected=selected,
                                   name=name,
                                   location=location,
                                   note=note,
                                   date=form_get('date'),
                                   start=form_get('start'),
                                   start_ampm=form_get('start_ampm'),
                                   end=form_get('end'),
                                   end_ampm=form_get('end_ampm'))
        # Check that the user is in this course
        if user.courses.filter_by(id=course_id).count() == 0:
            abort(403)
        # Again, user_id instead of owner_id
        new_event_record = Event(owner_id=user.id, course_id=course_id,
                name=name, location=location, start=start, end=end,
                note=note)
        db.session.add(new_event_record)
        g.user.events.append(new_event_record)
        db.session.commit()
        return redirect(url_for('event_view', event_id=new_event_record.id))


@app.route('/event/cancel/<int:event_id>')
@login_required
def event_remove(event_id):
    event = Event.query.get_or_404(event_id)
    if event.owner_id != g.user.id:
        abort(403)
    else:
        # TODO: may want to send out messages to all users annoucing
        # This might be unnecessary
        name = event.name
        db.session.delete(event)
        EventInvitation.query.filter_by(event_id=event.id).delete()
        db.session.commit()
        # Redirect to view all events
        flash("Deleted event " + event.name)
        return redirect(url_for('home'))


@app.route('/event/attend/<int:event_id>')
@login_required
def attend_event(event_id):
    event = Event.query.get_or_404(event_id)
    g.user.events.append(event)
    db.session.commit()

    flash("Now attending group")
    #return render_template('group/view.html')
    return redirect(url_for('event_view', event_id=event_id))


@app.route('/event/leave/<int:event_id>')
@login_required
def leave_event(event_id):
    event = Event.query.get_or_404(event_id)
    name = event.name
    if g.user.id == event.owner_id:
        db.session.delete(event)
    else:
        g.user.events.remove(event)
    db.session.commit()
    flash('Left Group')
    return redirect(url_for('event_view', event_id=event_id))


@app.route('/calendar')
@login_required
def calendar():
    events = []
    for course in g.user.courses.all():
        events.extend(course.events)
    event_json = events_to_json(events)
    return render_template('group/calendar.html', events_json=event_json)
