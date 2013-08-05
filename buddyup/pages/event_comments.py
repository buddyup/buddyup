from flask import g, request, redirect, url_for, session

from buddyup.app import app
from buddyup.database import Event, EventComment Course, EventMembership, db
from buddyup.templating import render_template
from buddyup.util import login_required

