import hashlib
import json
import random
import string
from flask import url_for, redirect, g, request, session, make_response

from buddyup.app import app
from buddyup.database import User, db
from buddyup.templating import render_template
from buddyup.util import login_required, shuffled, send_out_verify_email

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


from apiclient.discovery import build

# Google Specific
CLIENT_ID = json.loads(open('auth/client_secrets.json', 'r').read())['web']['client_id']
# SERVICE = build('plus', 'v1')


HOME_LIMIT = 24

# Expect behavior: '/' redirects to 

@app.route('/')
def index():
    if g.user is None:
        try:
            AUTHENTICATION_SCHEME = app.config['AUTHENTICATION_SCHEME'] or ""
            
            if AUTHENTICATION_SCHEME.lower() == "google":
                state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                              for x in xrange(32))
                session['state'] = state
                
                return render_template('social_login.html',
                                   CLIENT_ID=CLIENT_ID,
                                   STATE=state)
            else:
            
                # Note that this landing/intro "/" page is only used for testing/development.
                # For the production site, the landing/intro "/" page is hosted on weebly.
                ENABLE_AUTHENTICATION = app.config['BUDDYUP_ENABLE_AUTHENTICATION']
                all_users = User.query.order_by(User.user_name).all()
                all_usernames = [user.user_name for user in all_users]
                return render_template('cas_login.html',
                                       ENABLE_AUTHENTICATION=ENABLE_AUTHENTICATION,
                                       all_usernames=all_usernames,
                                       cas_service=app.cas_service)
        except:
            # An error that catastrophic should only happen with a brand new instance.
            return render_template('new_instance.html')

    else:
        return redirect(url_for('home'))


from sqlalchemy.sql.expression import func

def random_students():
    # This pulls from everyone in the database, not just coursemates.
    # If they have a photo, they are considered.
    return User.query\
            .filter(User.has_photos == True)\
            .filter(User.id != g.user.id)\
            .order_by(func.random())\
            .limit(HOME_LIMIT)

from os import environ
def preselected():
    if not environ.get("PRESELECTED_IDS"): return []
    ids = [int(id) for id in environ.get("PRESELECTED_IDS").split(',')]
    selected = shuffled(ids)[:HOME_LIMIT]
    return list(User.query.filter(User.id.in_(selected)))

from buddyup.pages.classmates import annotate_classmates

@app.route('/home')
@login_required
def home():
    classmates = preselected() or random_students()
    return render_template('index.html', classmates=annotate_classmates(classmates))


@app.route('/verify-email')
@login_required
def verify_email():
    next_page = request.args.get('next')
    return render_template('verify_email.html', next_page=next_page)

@app.route('/verify-email/<path:code>')
@login_required
def confirm_verify_email(code):
    print "confirm verify"
    print code
    print g.user

    if code and g.user.email_verify_code == code:
        g.user.email_verified = True
        db.session.commit()

    next_page = request.args.get('next')
    return render_template('verify_email.html', next_page=next_page)

@app.route('/send-verify-email')
@login_required
def send_verify_email():
    # Just in case they're in a funky account space, re-send this email.
    if not g.user.email_verify_code or g.user.email_verify_code == "":
        m = hashlib.sha1()
        m.update("Verify email for %s" % g.user.user_name)
        g.user.email_verify_code = u"%s" % m.hexdigest()
        db.session.commit()

    send_out_verify_email(g.user)

    return render_template('send_verify_email.html')


@app.route('/help')
@login_required
def help():
    return redirect('http://www.getbuddyup.com/faq.html')


@app.route('/suggestions')
@login_required
def suggestions():
    return render_template('setup/suggestions.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('setup/welcome.html')


@app.route('/connect', methods=['POST'])
def connect():
    """Exchange the one-time authorization code for a token and
    store the token in the session."""
    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user.
    if request.args.get('state', '') != session['state']:
      response = make_response(json.dumps('Invalid state parameter.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

    del session['state']
    code = request.data
    
    try:
      # Upgrade the authorization code into a credentials object
      # TODO: consoldiate references to that secrets file.
      oauth_flow = flow_from_clientsecrets('auth/client_secrets.json', scope='')
      oauth_flow.redirect_uri = 'postmessage'
      credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
      response = make_response(
          json.dumps('Failed to upgrade the authorization code.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

    # An ID Token is a cryptographically-signed JSON object encoded in base 64.
    # Normally, it is critical that you validate an ID Token before you use it,
    # but since you are communicating directly with Google over an
    # intermediary-free HTTPS channel and using your Client Secret to
    # authenticate yourself to Google, you can be confident that the token you
    # receive really comes from Google and is valid. If your server passes the
    # ID Token to other components of your app, it is extremely important that
    # the other components validate the token before using it.
    gplus_id = credentials.id_token['sub']
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
      response = make_response(json.dumps('Current user is already connected.'),
                               200)
      response.headers['Content-Type'] = 'application/json'
      return response

    # Store the access token in the session for later use.
    session['credentials'] = credentials.to_json()
    session['gplus_id'] = gplus_id

    response = make_response(json.dumps('Successfully connected user.', 200))
    response.headers['Content-Type'] = 'application/json'
    
    return response
