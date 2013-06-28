from datetime import datetime
from functools import partial

from buddyup.app import app
from buddyup.database import Event
from buddyup.templating import render_template
from buddyup.util import args_get


@app.route('/event/profile/<int:event_id>')
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
