from flask import g, request, flash, redirect, url_for, session, abort, get_flashed_message

# from datetime import datetime
# import time

from buddyup.app import app
from buddyup.database import Answer, Vote, db
# from buddyup.templating import render_template
from buddyup.util import login_required, form_get, check_empty

@app.route('/forum/answer/<int:answer_id>/+', methods = ['POST'])
@login_required
def up_vote(answer_id):
    vote = Vote.query.filter_by(user_id=g.user.id, answer_id=answer_id).first()
    if vote is None:
        new_vote_record = Vote(user_id=g.user.id, answer_id=answer_id, value=1)
        db.session.add(new_vote_record)
        db.session.commit()


@app.route('/forum/answer/<int:answer_id>/-', methods = ['POST'])
@login_required
def down_vote(answer_id):
    vote = Vote.query.filter_by(user_id=g.user.id, answer_id=answer_id).first()
    if vote is None:
        new_vote_record = Vote(user_id=g.user.id, answer_id=answer_id, value=-1)
        db.session.add(new_vote_record)
        db.session.commit()


@app.route('/forum/vote/remove/<int:vote_id>', methods = ['POST'])
@login_required
def remove_vote(answer_id):
    vote = Vote.query.filter_by(user_id=g.user.id, answer_id=answer_id).first()
    if vote is not None:
        vote.delete()
        db.session.commit()
