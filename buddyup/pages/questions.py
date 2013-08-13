from flask import g, request, flash, redirect, url_for, session, abort
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Question, Answer, Vote, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get, check_empty

@app.route('/forum')
def question_view_all():
    # TODO: display about 10 questions per page in chronological order.
    # Use pagination?
    pass

@app.route('/forum/<int:question_id>'):
    pass
