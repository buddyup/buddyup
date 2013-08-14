from flask import (g, request, flash, redirect, url_for, session, abort,
                   get_flashed_messages)
from datetime import datetime, timedelta
import time
from functools import partial
import re

from buddyup.app import app
from buddyup.database import Event, Course, EventMembership, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get, check_empty

TIME_REGEXP = re.compile(r"""
    (?P<hour>\d\d?)     # hour
    (?P<minute>:\d\d?)  # minute (optional)
""", flags=re.VERBOSE)
DATE_REGEXP = re.compile(r"""
    (?P<month>\d{1,2})[-/]  # month
    (?P<day>\d{1,2})[-/]    # day
    (?:20)?                 # optional '20' year prefix
    (?P<year>\d{2})         # year (xx)
""", flags=re.VERBOSE)


def parse_date(date, label):
    match = checked_match(DATE_REGEXP, date, label)
    if match:
        year = int(match.group('year')) + 2000
        month = int(match.group('month'))
        day = int(match.group('day'))
        return datetime(year, month, day)
    else:
        return None


def parse_time(time_string, ampm, base, label):
    match = checked_match(TIME_REGEXP, time_string, label)
    if match:
        hour = int(match.group('hour'))
        minute = int(match.group('minute')) or 0
        if ampm == 'am':
            hour -= 1
        elif ampm == 'pm':
            hour += 11
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
def event_view(event_id):
    event_record = Event.query.get_or_404(event_id)
    # No "owner" field in Event, instead "user_id"
    is_owner = event_record.user_id  == g.user.id
    remove_url = url_for('event_remove', event_id=event_record.id)
    return render_template('group/view.html',
                            event_record=event_record,
                            is_owner=is_owner,
                            remove_url=remove_url,
                            )


@app.route('/event/search')
def event_search():
    return render_template('group/search.html')


@app.route('/event/search_results')
def event_search_results():
    """
    Gives event_search_results.html a Pagination (see Flask-SQLAlchemy) of
    Events.
    
    Should this be GET?
    """

    get_int = partial(args_get, type=int)
    # TODO: Addition ordering?
    query = Event.query.order_by(Event.time)

    course = get_int('course')
    # -1 indicates no course selected, so don't filter
    if course >= 0:
        query = query.filter(Event.course == course)
    
    page = args_get('page', convert=int, default=0)
    if page < 0:
        page = 0
    else:
        page = page - 1

    if args_get('start_year') != '':
        start_year = get_int('start_year')
        start_month = get_int('start_month')
        start_day = get_int('start_day')
        start_hour = get_int('start_hour')
        start_minute = get_int('start_minute')
        
        end_year = get_int('end_year')
        end_month = get_int('end_month')
        end_day = get_int('end_day')
        end_hour = get_int('end_hour')
        end_minute = get_int('end_minute')

        # TODO: Timezone?
        start = datetime(start_year, start_month, start_day, start_hour, start_minute)
        end = datetime(end_year, end_month, end_day, end_hour, end_minute)
        # TODO: Show any event that overlaps the time
        query = query.filter(start < Event.start).filter(end > Event.end)

    return render_template('group/search_results.html',
                           pagination=query.pagination())

@app.route('/event/create', methods=['GET','POST'])
@login_required
def event_create():
    if request.method == 'GET':
        # TODO: pass out the user's course to set it as default
        return render_template('create_event.html', has_errors=False)
    else:
        user = g.user
        name = form_get('name')
        check_empty(name, "Event Name")
        course_id = form_get('course', convert=int)
        location = form_get('location', convert=int)
        check_empty(location, "Location")
        note = form_get('note')
        # Date
        date = parse_date(form_get('date'))

        # Start Time
        start = parse_time(form_get('start'), form_get('start_ampm'),
                           date, "Start")
        end = parse_time(form_get('end'), form_get('end_ampm'),
                         date, "End")
        

        if get_flashed_messages():
            return render_template('event/create.html', has_errors=True)

        # Check that the user is in this course
        if user.courses.filter_by(course_id==course_id).count() == 0:
            abort(403)
        # Again, user_id instead of owner_id
        new_event_record = Event(user_id=user.id, course_id=course_id,
                name=name, location_id=location, start=start, end=end,
                note=note)
        db.session.add(new_event_record)
        db.session.commit()
        #TODO: change this query to ensure it works as intended
        event_id = Event.query.filter_by(Event.name == name).first().id
        return redirect(url_for('event_view', event_id=event_id))

@app.route('/event/cancel/<int:event_id>')
@login_required
def event_remove(event_id):
    # Fixed: "event_id=event_id" into "id=event_id"
    event = Event.query.filter_by(id==event_id, owner_id==g.user.id)
    
    if event is None:
        abort(403)
    else:
        # TODO: may want to send out messages to all users annoucing
        # This might be unnecessary
        event.first().delete()
        db.session.commit()
        # Redirect to view all events
        return redirect(url_for('event_view'))

@app.route('/event/attend/<int:event_id>')
@login_required
def event_attend(event_id):
    event = Event.query.get_or_404(event_id)
    
    if is_attend(event_id):
        pass
    else:
        new_attendance_record = EventMembership(event_id=event_id,
                user_id=g.user.id)
        db.session.add(new_attendance_record)
        db.session.commit()
        # Not sure what's next
        pass


@app.route('/event/dismiss/<int:event_id>')
@login_required
def event_dismiss(event_id):
    event = Event.query.get_or_404(event_id)

    if is_attend(event_id):
        attendance_record = EventMembership.query.filter_by(event_id==event_id,
                user_id==g.user.id).first()
        attendance_record.delete()
        db.session.commit()
        # Not sure what's next
    else:
        abort(403)


@login_required
def is_attend(event_id):
    if EventMembership.query.filter_by(event_id==event_id,
            user_id==g.user.id).first() is None:
        return False
    else:
        return True
def calendar(start, end):
    query = Event.query
    query = query.filter(Event.time >= start)
    query = query.filter(Event.time <= end)
    return events_to_json(query.all())




@app.route('/calendar')
@login_required
def calendar():
    return events_to_json([])
