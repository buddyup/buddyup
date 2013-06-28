from urllib2 import urlopen, HTTPError
from urllib import urlencode, quote
from xml.etree import cElementTree as etree

from flask import url_for, request, redirect, flash, abort

from buddyup.app import app
from buddyup.database import User
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
        root=url_for('index'))


@app.route('/login')
def login():
    if 'ticket' in request.args:
        status, message = validate(args_get('ticket'))
        if status == 0:
            return redirect(url_for('/'))
        else:
            app.logger.error(message)
            abort(status)
    else:
        return redirect(app.cas_login)


@app.route('/logout')
def logout():
    # TODO: Some indication of success?
    request.session.clear()
    return redirect(app.cas_logout)


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
    except HTTPError as e:
        app.logger.error(
            "CAS validator request failed with status {code}: {reason}".format(
                code=e.code,
                reason=e.reason))
        return 500, "Error contacting CAS server"
    except etree.ParseError:
        return 500, "Bad response from CAS server: ParseError"

    failure_elem = tree.find(TAG_FAILURE)
    if failure_elem is not None:
        return 500, failure_elem.text.strip()

    success_elem = tree.find(TAG_SUCCESS)
    if success_elem is not None:
        user_name = success_elem.find(TAG_USER).text.strip()
        user_record = User.query.filter(User.user_name == user_name).first()
        # No user with that user name :(
        if user_record is None:
            # Maybe create the record?
            return 401, "User name not in database"
        request.session['user_id'] = user_record.id
        return True, None
    else:
        app.logger.error('bad response: %s', etree.tostring(tree.getroot()))
        return 500, "Bad response from CAS server: no success/failure"
