import random
import json
import string
from flask import url_for, redirect, g, request, session, make_response

from buddyup.app import app
from buddyup.database import User
from buddyup.templating import render_template
from buddyup.util import login_required, events_to_json, shuffled

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


from apiclient.discovery import build

# Google Specific
CLIENT_ID = json.loads(open('auth/client_secrets.json', 'r').read())['web']['client_id']
SERVICE = build('plus', 'v1')


HOME_LIMIT = 30

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
                
                return render_template('google_login.html',
                                   CLIENT_ID=CLIENT_ID,
                                   STATE=state)
            else:
            
                # Note that this landing/intro "/" page is only used for testing/development.
                # For the production site, the landing/intro "/" page is hosted on weebly.
                ENABLE_AUTHENTICATION = app.config['BUDDYUP_ENABLE_AUTHENTICATION']
                all_users = User.query.order_by(User.user_name).all()
                all_usernames = [user.user_name for user in all_users]
                return render_template('intro.html',
                                       ENABLE_AUTHENTICATION=ENABLE_AUTHENTICATION,
                                       all_usernames=all_usernames,
                                       cas_service=app.cas_service)
        except:
            # An error that catastrophic should only happen with a brand new instance.
            return render_template('new_instance.html')

    else:
        return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    # TODO: Possible scaling issue. Loads, shuffles, and listifies all classmates in memory? Can the DB handle this for us?
    # Calculate fellow students without duplicates.
    # SQLAlchemy ORM objects are unique to the session, not to an
    # individual query, so we can use a set.
    unordered_classmates = set()
    for course in g.user.courses.all():
        for other in course.users.filter(User.has_photos == True,
                                         User.id != g.user.id).all():
            unordered_classmates.add(other)

    classmates = shuffled(unordered_classmates)
    count = len(classmates)
    del classmates[HOME_LIMIT:]

    return render_template('index.html',
                           classmates=classmates,
                           count=count) 


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

@app.route('/term_and_conditions')
def term_conditions():
    return render_template('setup/term_conditions.html')




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


@app.route('/green/buddies')
@login_required
def green_buddies():
    return render_template('green/buddies/index.html')
