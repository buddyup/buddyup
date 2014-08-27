from functools import wraps
import re
import random
import json

from flask import flash, request, abort, g, redirect, url_for, request

from buddyup.database import (Course, Language, Event, EventComment, Visit, db, Action)
from buddyup.app import app, mandrill_client, in_production
from buddyup.photo import clear_images
import mandrill

_DEFAULT = object()


def track_activity(func):
    """
    Record the user's activity.
    """
    @wraps(func)
    def f(*args, **kwargs):
        if g.user is None: return
        entry = Action()
        entry.user_id = g.user.id
        entry.path = request.path
        entry.verb = request.method
        db.session.add(entry)
        db.session.commit()

        return func(*args, **kwargs)
    return f


def login_required(func):
    """
    Decorator to redirect the user to '/' if they are not logged in
    """
    @wraps(func)
    def f(*args, **kwargs):
        if g.user is None:
            app.logger.info('redirecting not logged in user')
            return redirect(url_for('index'))
        elif not g.user.initialized and f.__name__ != 'profile_create':
            return redirect(url_for('profile_create'))
        else:
            return func(*args, **kwargs)
    return f


def _parameter_get(source, var, convert=None, default=_DEFAULT):
    # Get a 
    # source: mapping type
    # var: variable name
    # convert: function to call on variable (includes int, float, etc.)
    # default: Default value
    if var not in source:
        if default is _DEFAULT:
            app.logger.info("Required form parameter [%s] does not exist; source=%s" % (var, source))
            abort(400)
            # abort raises an exception, so the function ends here
        else:
            return default
    elif convert is not None:
        try:
            return convert(source[var])
        except ValueError:
            app.logger.info("ValueError when converting variable %s", var)
            abort(400)
    else:
        return source[var]


def form_get(var, convert=None, default=_DEFAULT):
    """
    Get a variable from request.form. Abort with status code 400 if the
    variable is not present unless default is given.
    
    convert is a function or class to convert the value. 
    
    If specified, default is used instead of raising an error.
    """
    
    return _parameter_get(request.form, var, convert, default)


def args_get(var, convert=None, default=_DEFAULT):
    """
    Get a variable from request.args. Abort with status code 400 if the
    variable is not present unless default is given.
    
    convert is a function or class to convert the value. 
    
    If specified, default is used instead of raising an error.
    """
    
    return _parameter_get(request.args, var, convert, default)


def check_empty(value, label):
    """
    Check if a string is empty, flash a message if it is.
    """
    if value == u'':
        flash(label + " Is Empty")


def checked_regexp(regexp, value, label):
    """
    Check if a regular expression matches, flash a message if it didn't.
    `regexp` is either a string or compiled regular expression.
    """
    if isinstance(regexp, (unicode, str)):
        match = re.match(regexp, value)
    else:
        match = regexp.match(value)
    if match is None:
        flash(label + " Is Incorrectly Formatted")
        return None
    else:
        return match


def check_course_membership(course, user=None):
    """
    Check that the given user belongs to the course. Defaults to g.user.
    Aborts with a 403 on error.
    """
    if user is None:
        user = g.user

    if isinstance(course, Course):
        course_id = course.id
    else:
        course_id = course

    if user.courses.filter(Course.id == course_id).count() == 0:
        abort(403)


def events_to_json(events):
    """
    Convert a list/iterable of events records to a list that can be converted
    to json to work with the fullcalendar widget. In the template, use::
    
        events: {{ events|tojson|safe }}
    """
    json = []
    for event in events:
        json.append({
            'id': event.id,
            'title': event.name,
            'start': event.start.strftime("%Y-%m-%d %H:%M"),
            'end': event.end.strftime("%Y-%m-%d %H:%M"),
            'url': url_for('event_view', event_id=event.id),
        })
    return json


@app.template_global()
@app.template_filter()
def email(user):
    return user.email or default_email(user)

@app.template_global()
@app.template_filter()
def fix_url(url):
    return url if url and ( url.lower().startswith("http://") or url.lower().startswith("https://") ) else "http://%s" % url

def sorted_languages():
    """
    Get all languages sorted, with English always as the first language.
    """
    # Python 3: Use functools.cmp_to_key
    def compare(a, b):
        if a.name == u"English":
            return -1
        elif b.name == u"English":
            return 1
        else:
            return cmp(a, b)
    return sorted(Language.query.all(), cmp=compare)


@app.template_global()
def default_email(user=None):
    if user is None:
        user = g.user
    return app.config['DEFAULT_EMAIL_FORMAT'].format(user=user.user_name)


def update_relationship(rel, records):
    current = {record.id: record for record in rel.all()}
    new = {record.id: record for record in records}

    # Python 3: viewkeys() -> keys()
    insert_ids = new.viewkeys() - current.viewkeys()
    for id in insert_ids:
        rel.append(new[id])
    
    remove_ids = current.viewkeys() - new.viewkeys()
    for id in remove_ids:
        rel.remove(current[id])


def shuffled(iterable):
    l = list(iterable)
    random.shuffle(l)
    return l


def send_mandrill_email_message(user_recipient, subject, html):
    IP_POOL = 'Main Pool'
    FROM_EMAIL = 'noreply@getbuddyup.com'
    FROM_NAME = 'Buddyup noreply'
    try:
        message = {'from_email': FROM_EMAIL,
                   'from_name': FROM_NAME,
                   'headers': {'Reply-To': FROM_EMAIL},
                   'html': html,
                   'subject': subject,
                   'to': [{'email': email(user_recipient),
                           'name': user_recipient.full_name,
                           'type': 'to'}],}

        if in_production():
            mandrill_client.messages.send(message=message, async=False,
                                               ip_pool=IP_POOL)
        else:
            with open("last_sent.msg", "w") as msgfile:
                msgfile.write(json.dumps(message))

    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
        raise


def get_domain_name():
    return app.config.get('DOMAIN_NAME', 'buddyup.herokuapp.com')


def delete_user(user):
    def delete_records(records):
        for record in records:
            db.delete(record)
    delete_records(user.buddy_invitations_sent)
    delete_records(user.buddy_invitations_received)
    delete_records(user.event_invitations_sent)
    delete_records(user.event_invitations_received)
    Event.query.filter_by(owner_id=user.id).delete()
    EventComment.query.filter_by(user_id=user.id).delete()
    Visit.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    clear_images(user)


from datetime import datetime
def epoch_milliseconds(when):
    if not when: return 0
    epoch = datetime.utcfromtimestamp(0)
    delta = when - epoch
    return int(delta.total_seconds() * 1000)


def calendar_event(event):
    return {
	    'id': "%s" % event.id,
        'title': event.name,
        'start': unicode(epoch_milliseconds(event.start)),
        'end': unicode(epoch_milliseconds(event.end)),
		'url': "/courses/%s/events/%s" % (event.course_id, event.id),
        'class': 'event-warning',
    }

def easy_datetime(date_string):
    """
    Format MUST match this without deviation: "Mar 15 2014 15:00"
    """
    return datetime.strptime(date_string, "%b %d %Y %H:%M")














