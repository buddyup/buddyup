from flask import render_template as _render_template
from flask import session, request, g

from buddyup import app, database, util


@app.template_global
def paragraphs(string):
    """
    Convert a newline separated string to a list of paragraph strings.
    ::

        {% for p in message.text|paragraphs %}
            <p>{{ p }}</p>
        {% endfor %}
    """
    return [line.strip() for line in string.split('\n')]


@app.template_global
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


@app.template_global
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
        'id': event.id
        'location': event.location,
    }
    if datef:
        variables['start_date'] = event.start.strftime(datef)
        variables['end_date'] = event.end.strftime(datef)
    
    if timef:
        variables['start_time'] = event.start.strftime(timef)
        variables['end_time'] = event.end.strftime(timef)
    
    return format.format(**variables)


@app.template_global
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


def render_template(template, **variables):
    """
    Wrapper around flask.render_template to add in some extra variables.
    See doc/template.rst
    """
    # g.user is constructed in app.py's setup()
    variables['user_record'] = g.user
    variables['logged_in'] = g.user is not None

    return _render_template(template, **variables)
