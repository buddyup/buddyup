from urllib2 import urlopen, URLError
from urllib import urlencode
from xml.etree import cElementTree as etree

from flask import url_for, request

from buddyup import app

VALIDATE_URL = "{server}/serviceValidate?{args}"


@app.before_first_request
def setup_cas():
    # Cache various URL's
    app.cas_server = app.config['CAS_SERVER']
    app.cas_service = url_for('login', external=True)
    app.cas_login = "{server}?service={service}".format(
        server=app.cas_server,
        service=quote(app.cas_service))


@app.route('/login')
def login():
    if 'ticket' in request.args:
        status, message = validate(request.args.ticket):
        if status == 0:
            return redirect(url_for('/'))
        else:
            flash(message)
            abort(status)
    else:
        return redirect(app.cas_login)


@app.route('/logout')
def logout():
    # TODO: Some indication of success?
    request.session.clear()
    redirect(url_for('/'))


def validate(ticket):
    """
    Validate the given ticket against app.config['CAS_HOST'] and set
    session variables.
    
    
    Returns (status, message)
    
    status: Desired HTTP status. 0 on success
    message: Message on failure, None on success
    """

    cas_server = app.cas_server
    service = quote(app.cas_service)
    args = urllib.urlencode({
        'service': service,
        'ticket': ticket})
    url = VALIDATE_URL.format(server=cas_server,
                              args=urlencode(args))
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
        app.logger.error("CAS validator response is invalid XML")
        return 500, "Bad response from CAS server: ParseError"

    failure_elem = tree.find('cas:authenticationFailure')
    if failure_elem is not None:
        return 401, failure_elem.text

    success_elem = tree.find('cas:authenticationSuccess')
    if success is not None:
        user_name = success_elem.find('cas:user').text
        user_record = User.query.filter(User.user_name == user_name)
        request.session['user_id'] = user_record.id
        return True, None
    else:
        app.logger.log()
        return 500, "Bad response from CAS server: no success/failure"
