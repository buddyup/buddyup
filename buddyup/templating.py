from flask import render_template as _render_template
from flask import session, request

from buddyup import app, database, util

TEMPLATE_FUNCTIONS = [util.url_for_user, util.url_for_group,
                      util.url_for_event, util.url_for_course]

template_extras = {}
for f in TEMPLATE_FUNCTIONS:
    template_extras[f.__name__] = f


def render_template(template, **kwargs):
    """
    Wrapper around flask.render_template to add in some extra variables.
    
    user: None [invalid or no session] or instance of buddyup.database.User
    """
    if 'uid' in request.session:
        user_id = request.session['uid']
        user = database.User.query.get(user_id)
        kwargs['user_record'] = user
    else:
        kwargs['user_record'] = None
    kwargs.update(template_extras)
    return _render_template(template, **kwargs)


