# Template wrapper and basic helper functions
# See also: buddyup.photo.photo_*

from ConfigParser import ConfigParser

from flask import render_template as _render_template
from flask import g, url_for

from buddyup.app import app
from buddyup.database import User, Event

STATIC_ALIASES_INI = "buddyup/aliases.ini"


app.add_template_global(zip)


@app.template_filter()
@app.template_global()
def paragraphs(string):
    """
    Convert a newline separated string to a list of paragraph strings.
    ::

        {% for p in message.text|paragraphs %}
            <p>{{ p }}</p>
        {% endfor %}
    """
    return [line.strip() for line in string.split('\n')]


@app.template_global()
def format_course(course, format):
    """
    Render a buddyup.database.Course according to a format string in the style::
    
        {subject} {number}
    
    Variables:
    * id
    * crn
    * subject
    * number
    * section
    """
    return format.format(
        id=course.id,
        crn=course.crn,
        subject=course.subject,
        number=course.number,
        section=course.section,
        )


@app.template_global()
def format_event(event, format, datef=None, timef=None):
    """
    Render a buddyup.database.Event according to a format string. Pass in
    datef and/or timef to get formatted dates/times.
    
    datef and timef are in the style of Python's datetime.strftime. See:
    
    http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    
    Variables:
    * id
    * location
    * start_date (if datef is passed in)
    * end_date (if datef is passed in)
    * start_time (if timef is passed in)
    * end_time (if timef is passed in)
    """

    variables = {
        'id': event.id,
        'location': event.location,
    }
    if datef:
        variables['start_date'] = event.start.strftime(datef)
        variables['end_date'] = event.end.strftime(datef)
    
    if timef:
        variables['start_time'] = event.start.strftime(timef)
        variables['end_time'] = event.end.strftime(timef)
    
    return format.format(**variables)


@app.template_global()
def format_user(user, format):
    """
    Render a buddyup.database.Event according to a format string
    
    Variables:
    * id
    * user_name
    * full_name
    """

    return format.format(
        id=user.id,
        user_name=user.user_name,
        full_name=user.full_name,
        )


cdn_locations = {}
local_locations = {}


@app.before_first_request
def load_aliases():
    cp = ConfigParser()
    cp.read(STATIC_ALIASES_INI)
    use_cdn = app.config['USE_CDN']
    for file_name in cp.sections():
        if use_cdn and cp.has_option(file_name, 'cdn'):
            cdn_locations[file_name] = cp.get(file_name, 'cdn')
        if cp.has_option(file_name, 'local'):
            local_locations[file_name] = cp.get(file_name, 'local')


def _static_shortcut(prefix, filename):
    if filename in cdn_locations:
        return cdn_locations[filename]
    else:
        filename = local_locations.get(filename, filename)
        return url_for('static', filename='{prefix}/{filename}'.format(
            prefix=prefix, filename=filename))


@app.template_global()
def js(filename):
    """
    Look up the preferred location of the specified JavaScript file. File
    names without a trailing ".js" will have it automatically added.
    """
    if not filename.endswith(".js"):
        filename += '.js'
    return _static_shortcut('js', filename)


@app.template_global()
def css(filename):
    """
    Look up the preferred location of the specified CSS file. File names
    without a trailing ".css" will have it automatically added.
    """
    if not filename.endswith(".css"):
        filename += '.css'
    return _static_shortcut('css', filename)


@app.template_global()
def img(filename):
    return _static_shortcut('img', filename)


@app.template_global()
def profile(record):
    if isinstance(record, Event):
        return url_for('event_view', event_id=record.id)
    elif isinstance(record, User):
        return url_for('buddy_view', user_name=record.user_name)
    else:
        raise TypeError("profile(record) requires an Event or User, not %s" %
                        record.__class__.__name__)


@app.template_global()
def view_url(record):
    """view_url(record) -> str
    View URL for a given record (User or Event)
    """
    if isinstance(record, User):
        return url_for('buddy_view', user_name=record.user_name)
    elif isinstance(record, Event):
        return url_for('event_view', event_id=record.id)
    else:
        raise TypeError("Unknown type '%s'" % record.__class__.__name__)


def render_template(template, **variables):
    """
    Wrapper around flask.render_template to add in some extra variables.
    See doc/template.rst
    """
    # g.user is constructed in app.py's setup()
    variables['user_record'] = g.user
    variables['logged_in'] = g.user is not None
    variables['login_url'] = app.cas_login
    if g.user:
        variables['user_name'] = g.user.full_name
    else:
        variables['user_name'] = u''
    if g.user is None:
        variables['is_admin'] = None
    else:
        # TODO: Be able to mark users as admins
        variables['is_admin'] = g.user.user_name == app.config.get("ADMIN_USER", u"")

    return _render_template(template, **variables)
