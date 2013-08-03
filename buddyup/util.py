from functools import wraps

from flask import url_for, request, abort, g, redirect

from buddyup import database
from buddyup.app import app

_DEFAULT = object()


def login_required(func):
    @wraps(func)
    def f(*args, **kwargs):
        if g.user is None:
            return redirect('login')
        else:
            return func(*args, **kwargs)


@app.template_global
def url_for_user(user, **kwargs):
    return _url_for_profile(user, 'user_view', database.User, kwargs)


@app.template_global
def url_for_event(event, **kwargs):
    return _url_for_profile(event, 'event_view', database.Event, kwargs)


@app.template_global
def url_for_course(course, **kwargs):
    return _url_for_profile(course, 'course_view', database.Course, kwargs)


def _url_for_profile(id, base, kls, kwargs):
    # base: url_for(base)
    # profile_id: id number or instance of kls
    # kls: Viewable profile from buddyup.database
    # returns str
    if isinstance(id, kls):
        id = id.id
    return "%s/profile/%i" % (url_for(base), id)


def _parameter_get(source, var, convert=None, default=_DEFAULT):

    if var not in source:
        if default is _DEFAULT:
            print "OMG"
            abort(400)
            # abort raises an exception, so the function ends here
        else:
            return default
    elif convert is not None:
        try:
            return convert(source[var])
        except ValueError:
            print "OMG"
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
