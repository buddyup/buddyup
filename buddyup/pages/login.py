from urllib2 import urlopen, URLError
from urllib import urlencode, quote
from xml.etree import cElementTree as etree
import hashlib
import json
import os

import requests

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask import url_for, request, redirect, flash, abort, session

from buddyup.app import app
from buddyup.database import User, Visit, db
from buddyup.util import args_get, login_required

VALIDATE_URL = "{server}/serviceValidate?{args}"
CAS_NS = 'http://www.yale.edu/tp/cas'
TAG_SUCCESS = './/{%s}authenticationSuccess' % CAS_NS
TAG_FAILURE = './/{%s}authenticationFailure' % CAS_NS
TAG_USER = './/{%s}user' % CAS_NS


@app.before_first_request
def setup_cas():
    if not use_cas(): return
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

def use_google():
    return (app.config.get('AUTHENTICATION_SCHEME', "").lower() == "google")


def create_new_user(user_name):
    new_user = User(user_name=user_name)
    m = hashlib.sha1()
    m.update("Verify email for %s" % user_name)
    new_user.email_verify_code = u"%s" % m.hexdigest()
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
    elif use_google() and 'gplus_id' in session:
        user_name = session['gplus_id']
    else:
        # TODO: This should be an explicit case (based on environment)
        # NOT a fall-through case:
        # Authentication is disabled, so just log the user in.
        user_name = args_get('username')

    destination = 'home'

    existing_user = User.query.filter(User.user_name == user_name).first()

    if not existing_user:
        existing_user = create_new_user(user_name)
        destination = 'welcome'

    establish_session(existing_user)

    record_visit(existing_user)

    return redirect(url_for(destination))


@app.route('/logout')
@login_required
def logout():
    destination = url_for('index')

    if app.config.get('BUDDYUP_ENABLE_AUTHENTICATION', True):
        # Accommodate PDX dual-domains for now. TODO: Pull this once we're only using pdx.buddyup.org
        destination = app.cas_logout if "pdx.buddyup.org" not in request.url_root else app.cas_logout.replace("buddyup.herokuapp.com", "pdx.buddyup.org")
    elif use_google():
        # Toss our Google key
        disconnect()
        # And if we're demoing, log them out of Google altogether
        # so that the next person can login fresh.
        if app.config.get('DEMO_MODE', "").lower() == "true":
            destination = "https://accounts.google.com/Logout"

    session.clear()
    return redirect(destination)
    


def validate(ticket):
    """
    Validate the given ticket against app.config['CAS_HOST'] and set
    session variables.
    
    
    Returns (status, message)
    
    status: Desired HTTP status. 0 on success
    message: Message on failure, None on success
    """

    cas_server = app.cas_server
    service = app.cas_service if "pdx.buddyup.org" not in request.url_root else app.cas_service.replace("buddyup.herokuapp.com", "pdx.buddyup.org")
    args = {
        'service': service,
        'ticket': ticket
    }
    url = VALIDATE_URL.format(server=cas_server,
                              args=urlencode(args))
    # app.logger.info("Validating at URL " + url)
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

import httplib2
import json

def disconnect():
    # Google-specific, for logout.
    if not session.get('credentials'): return

    credentials = json.loads(session.get('credentials'))

    # Ask Google to revoke the current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials['access_token']
    result = httplib2.Http().request(url, 'GET')[0]

    if result['status'] == '200':
        del session['credentials']


def have_api_keys(env):
    return set(["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET", "AUTH0_CALLBACK_URL"]).issubset(env.keys())


# From https://docs.auth0.com/#!/web/python

# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    env = os.environ
    code = request.args.get('code')

    if not have_api_keys(env):
        return render_template('new_instance.html')

    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(domain=env["AUTH0_DOMAIN"])
    token_payload = {
        'client_id' : env['AUTH0_CLIENT_ID'], \
        'client_secret' : env['AUTH0_CLIENT_SECRET'], \
        'redirect_uri' : env['AUTH0_CALLBACK_URL'], \
        'code' : code, \
        'grant_type': 'authorization_code' \
    }

    token_info = requests.post(token_url, data=json.dumps(token_payload), headers = json_header).json()
    try:
        user_url = "https://{domain}/userinfo?access_token={access_token}".format(
        domain=env["AUTH0_DOMAIN"],
        access_token=token_info['access_token']
        )
    except Exception, e:
        print token_info
        raise e

    user_info = requests.get(user_url).json()

    existing_user = User.query.filter(User.user_name == user_info['user_id']).first()

    destination = 'home'
    if not existing_user:
        existing_user = create_new_user(user_info['user_id'])
        existing_user.full_name = user_info["name"]
        if "email" in user_info:
            existing_user.email = user_info["email"]
        existing_user.user_name = user_info["user_id"]
        
        m = hashlib.sha1()
        m.update("Verify email for %s" % user_info["user_id"])
        existing_user.email_verify_code = m.hexdigest()
        db.session.commit()
        destination = 'welcome'
    else:
        if not existing_user.email_verify_code:
            m = hashlib.sha1()
            m.update("Verify email for %s" % user_info["user_id"])
            existing_user.email_verify_code = m.hexdigest()
            db.session.commit()

    establish_session(existing_user)
    # We're saving all user information into the session
    session['profile'] = user_info

    record_visit(existing_user)


    # Redirect to the User logged in page that you want here
    return redirect(url_for(destination))
