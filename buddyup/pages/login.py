from urllib2 import urlopen, URLError
from urllib import urlencode, quote
from xml.etree import cElementTree as etree

from flask import url_for, request, redirect, flash, abort, session

from buddyup.app import app
from buddyup.database import User, Visit, db
from buddyup.util import args_get

VALIDATE_URL = "{server}/serviceValidate?{args}"
CAS_NS = 'http://www.yale.edu/tp/cas'
TAG_SUCCESS = './/{%s}authenticationSuccess' % CAS_NS
TAG_FAILURE = './/{%s}authenticationFailure' % CAS_NS
TAG_USER = './/{%s}user' % CAS_NS


@app.before_first_request
def setup_cas():
    # Cache various URL's
    app.cas_server = app.config['CAS_SERVER']
    app.cas_service = url_for('login', _external=True)
    app.logger.info("Setting CAS service to %s", app.cas_service)
    app.cas_login = "{server}/login?service={service}".format(
        server=app.cas_server,
        service=quote(app.cas_service))
    app.logger.info("Setting CAS log URL to %s", app.cas_login)
    app.cas_logout = "{server}/logout?url={root}".format(
        server=app.cas_server,
        root=url_for('index', _external=True))


def use_cas():
    return app.config.get('BUDDYUP_ENABLE_AUTHENTICATION', True)

def create_new_user(user_name):
    new_user = User(user_name=user_name)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def record_visit(user):
    db.session.add(Visit(user_id=user.id))
    db.session.commit()

def establish_session(user):
    session['user_id'] = user.id

LOGIN_OK = 0

@app.route('/login')
def login():
    if ('ticket' not in request.args) and use_cas():
        return redirect(app.cas_login)

    if use_cas():
        status, payload = validate(ticket=args_get('ticket'))
        if status != LOGIN_OK:
            app.logger.error(payload)
            abort(status)
        user_name = payload
    else:
        # Authentication is disabled, so just log the user in.
        _, user_name = LOGIN_OK, args_get('username')

    destination = 'home'

    existing_user = User.query.filter(User.user_name == user_name).first()

    if not existing_user:
        existing_user = create_new_user(user_name)
        destination = 'welcome'

    establish_session(existing_user)

    record_visit(existing_user)

    return redirect(url_for(destination))


@app.route('/logout')
def logout():
    # TODO: Some indication of success?
    session.clear()
    if app.config.get('BUDDYUP_ENABLE_AUTHENTICATION', True):
        return redirect(app.cas_logout)
    else:
        return redirect(url_for('index'))


def validate(ticket):
    """
    Validate the given ticket against app.config['CAS_HOST'] and set
    session variables.
    
    
    Returns (status, message)
    
    status: Desired HTTP status. 0 on success
    message: Message on failure, None on success
    """

    cas_server = app.cas_server
    service = app.cas_service
    args = {
        'service': service,
        'ticket': ticket
    }
    url = VALIDATE_URL.format(server=cas_server,
                              args=urlencode(args))
    app.logger.info("Validating at URL " + url)
    try:
        req = urlopen(url)
        tree = etree.parse(req)
    except URLError as e:
        return 500, "Error contacting CAS server: {}".format(e)
    except etree.ParseError:
        return 500, "Bad response from CAS server: ParseError"

    failure_elem = tree.find(TAG_FAILURE)
    if failure_elem is not None:
        return 500, "Failure: " + failure_elem.text.strip()

    success_elem = tree.find(TAG_SUCCESS)
    if success_elem is not None:
        user_name = success_elem.find(TAG_USER).text.strip()
        return 0, user_name
    else:
        app.logger.error('bad response: %s', etree.tostring(tree.getroot()))
        return 500, "Bad response from CAS server: no success/failure"
