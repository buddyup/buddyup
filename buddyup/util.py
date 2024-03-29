from functools import wraps
import re
import random
import json

from flask import flash, request, abort, g, redirect, url_for, request
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.widgets import ListWidget, CheckboxInput, HTMLString, RadioInput

from buddyup.database import (Course, Language, Event, EventComment, Visit, db, Action, User, Tutor, TutorCourse, TutorLanguage)
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
        elif not g.user.initialized and f.__name__ not in ['profile_create','logout']:
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


def send_email(user_recipient, subject, text):
    IP_POOL = 'Main Pool'
    FROM_EMAIL = 'noreply@buddyup.org'
    FROM_NAME = 'BuddyUp'
    try:
        message = {'from_email': FROM_EMAIL,
                   'from_name': FROM_NAME,
                   'headers': {'Reply-To': FROM_EMAIL},
                   'text': text,
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

def send_out_verify_email(user):
    invite_info = {
            'NAME': user.full_name,
            'RECIPIENT': user.email,
            'DOMAIN': app.config.get('DOMAIN_NAME', ''),
            'CODE': user.email_verify_code
        }

    subject = "Verify your email with BuddyUp!"
    message = """Hi {NAME},

Welcome to BuddyUp!  

To keep BuddyUp safe, we require that you verify your .edu email to continue using BuddyUp, by clicking the link below.

http://{DOMAIN}/verify-email/{CODE}

Thanks,

The BuddyUp Team""".format(**invite_info)

    send_email(user, subject, message)


# TODO: Add boolean to deactivate users instead of deleting them.
# This code is relatively untested and shouldn't be considered production-quality.
def delete_user(user):
    if Tutor.query.filter_by(user_id=user.id).count() > 0:
        print "Clear Tutors table first."
        return

    def delete_records(records):
        for record in records:
            db.delete(record)
    # TODO: Cascades for some of this?
    delete_records(user.buddy_invitations_sent)
    delete_records(user.buddy_invitations_received)
    delete_records(user.event_invitations_sent)
    delete_records(user.event_invitations_received)

    Action.query.filter_by(user_id=user.id).delete()
    Event.query.filter_by(owner_id=user.id).delete()
    EventComment.query.filter_by(user_id=user.id).delete()
    Visit.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    clear_images(user)


from datetime import datetime
@app.template_global()
def epoch_time(when):
    """
    Seconds since epoch (Jan 1, 1970)
    """
    if not when: return 0
    epoch = datetime.utcfromtimestamp(0)
    delta = when - epoch
    return int(delta.total_seconds())

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


def list_of_times():
    return [t for t in range(0, 86400, 1800)]

DAY_LENGTH = 86400
MIDNIGHT = 0
NOON = DAY_LENGTH / 2
HOUR = 3600

def time_from_timestamp(timestamp):
    """
    'timestamp' represents a half-hour segement of time in the day.
    It is represented as seconds since midnight. Here we return a tuple
    of both the timestamp and a string with the equivalent time.
    """
    hour = (timestamp // HOUR) or 12
    if hour > 12:
        hour = hour - 12
    meridian = ["AM", "PM"][timestamp >= NOON]

    minutes = ["30", "00"][timestamp % HOUR == 0 or timestamp == 0]
    timestr = "%s:%s%s" % (hour, minutes, meridian)
    return timestamp, timestr

def time_pulldown():
    return [time_from_timestamp(time) for time in list_of_times()]


def acting_on_self(user):
    return user.id == g.user.id

from buddyup.database import Notification

def send_notification(sender, recipient, payload, **kwargs):

    notification = Notification(sender_id=sender.id, recipient_id=recipient.id)

    notification.payload = payload
    notification.action_text = kwargs['action_text'] if 'action_text' in kwargs else ""
    notification.action_link = kwargs['action_link'] if 'action_link' in kwargs else ""

    db.session.add(notification)
    db.session.commit()


@app.template_global()
@app.template_filter()
def date_short(time):
    return time.strftime("%b %d") if time else ""

@app.template_global()
@app.template_filter()
def date_long(time):
    return time.strftime("%b %d, %Y") if time else ""


@app.template_global()
@app.template_filter()
def date_and_time(time):
    # June 31 - 5:32PM
    return time.strftime("%B %d, %I:%M%p") if time else ""



#----------------------------------------------------------------------------
# Demo & Diagnostic support methods
#----------------------------------------------------------------------------
import urllib
def wipe_user(user_name):
    """
    Remove the user and everything associated with that user. Helpful
    with testing/demoing the login system.
    """
    user_name = urllib.unquote(user_name) # Username is coming straight from the url bar.
    user = User.query.filter(User.user_name==user_name).first()
    delete_user(user)

def populate_event(event_id):
    """
    Create some attendees for the event.
    """
    event = Event.query.get(event_id)
    users = User.query.filter(User.has_photos==True).limit(10)
    for user in users:
        user.events.append(event)
    db.session.commit()


class ListCheckboxWidget(ListWidget):
  """ ListWidget doesn't do rendering properly with Twitter Bootstrap's CSS. """

  def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)

    html = ["\n"]

    for subfield in field:
      html.append(u'<label class="checkbox-inline">%s%s</label>\n' % (subfield(), subfield.label.text))

    return HTMLString(u''.join(html))

#  Form Stuff
class QueryMultiCheckboxField(QuerySelectMultipleField):
  """
    A multiple-select, except displays a list of checkboxes.
    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
  """

  widget = ListCheckboxWidget()
  option_widget = CheckboxInput()

  def iter_choices(self):
    """ Handle True/False checkboxes in a single list. """

    for pk, obj in self._get_object_list():
      if hasattr(obj, self.id):
        selected = getattr(obj, self.id)
      else:
        selected = obj in self.data

      yield (pk, self.get_label(obj), selected)

class ListRadioWidget(ListWidget):
  def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)

    html = ["\n"]

    for subfield in field:
      html.append(u'<label class="radio">%s%s</label>\n' % (subfield(), subfield.label.text))

    return HTMLString(u''.join(html))

#  Form Stuff
class QueryRadioField(QuerySelectField):
  """
    A select, except displays a list of Radioes.
  """

  widget = ListRadioWidget()
  option_widget = RadioInput()
