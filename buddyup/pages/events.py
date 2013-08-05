from flask import g, request, flash, redirect, url_for, session
from datetime import datetime
from functools import partial

from buddyup.app import app
from buddyup.database import Event, Course, EventMembership, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get


@app.route('/event')
@login_required
def event_view():
    # TODO: view all events that relates to the currently active user
    events = g.user.events
    return render_template('event_view.html', events=events)

@app.route('/event/<int:event_id>')
def event_view(event_id):
    event_record = Event.query.get_or_404(event_id)
    return render_template('event_view.html',
                            event_record=event_record)


@app.route('/event/search')
def event_search():
    return render_template('event_search.html')


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

    return render_template('event_search_results.html',
                           pagination=query.pagination())

@app.route('event/create', methods=['GET','POST'])
@login_required
def even_create():
    if request.method == 'GET':
        # TODO: pass out the user's course to set it as default
        return render_template('create_event.html')
    else:
        user = g.user
        error = False
        name = form_get('name')
        if name == '':
            flash("Event Name Is Empty")
            error = True
        course = form_get('course')
        location = form_get('location')
        if location == '':
            flash("Location Is Empty")
            error = True
        # TODO: get starting and ending time
        start = form_get('start')
        if start is None:
            flash("Starting Time Is Empty")
            error = True
        end = form_get('end')
        if end is None:
            flash("Ending Time Is Empty")
            error = True
        note = form_get('note')

        if error:
            return render_template('create_event.html')
        
        # TODO: magic to conver start and end into DateTime
        course_id = Course.query.filter_by(Course.name == course).first().id
        # TODO: may want to check if this active user is in that course
        new_event_record = Event(owner_id=user.id, course_id=course_id,
                name=course, location=location, start=start, end=end,
                note=note)
        db.session.add(new_event_record)
        db.session.commit()
        event_id = Event.query.filter_by(Event.name == name).first().id
        return redirect(url_for(event_view(event_id)))

@app.route('/event/cancel/<int:event_id>', methods=['POST'])
@login_required
def event_remove(event_id):
    event = Event.query.filter_by(Event.event_id=event_id,
            Event.owner_id=g.user.id)
    # If the user is not the owner, 403!
    if event is None:
        abort(403)
    else:
        # TODO: may want to send out messages to all users annoucing
        # This might be unnecessary
        EventMembership.query.filter_by(EventMembership.event_id=event_id).delete()
        db.session.delete(event)
        db.session.commit()
        return redirect(url_for(event_view()))
    #pass
