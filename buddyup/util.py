from functools import wraps
import re

from flask import flash, request, abort, g, redirect, url_for

from buddyup.database import Course, Language
from buddyup.app import app

_DEFAULT = object()


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
    return user.email or (user.user_name + u"@pdx.edu")


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
@app.template_globals()
def rowize(items, width):
    """
    Slice a list into a list of uniform sized lists::
    
        >>> rowize([1, 2, 3, 4], 3)
        [[1, 2, 3], [4]]
    """
    assert width > 0, "Zero width row size"

    return [items[i:i + width] for i in range(0, len(items), width)]
