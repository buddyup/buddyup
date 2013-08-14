from functools import wraps
import re

from flask import flash, request, abort, g, redirect, url_for

from buddyup import database
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
            abort(400)
            # abort raises an exception, so the function ends here
        else:
            return default
    elif convert is not None:
        try:
            return convert(source[var])
        except ValueError:
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
    


def events_to_json(events):
    json = []
    for event in events:
        date = event.date.strftime("%Y-%m-%d %H:%M")
        json.append({
            'id': event.id,
            'title': event.name,
            'start': date,
            'end': date,
            'url': url_for('event_view', event_id=event.id),
        })
    return json