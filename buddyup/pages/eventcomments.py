from flask import g, request, redirect, url_for, session, abort
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Event, EventComment, Course, EventMembership, db
from buddyup.templating import render_template
from buddyup.util import login_required, form_get, check_empty
from buddyup.pages.events import event_view

@app.route('/event/comment/create/<int:event_id>', methods=['GET', 'POST'])
@login_required
def post_comment(event_id):
    event_record = Event.query.get_or_404(event_id)
    if request.method == 'GET':
        return render_template('create_comment.html', has_errors=False)
    else:
        user = g.user
        title = form_get('title')
        check_empty(title, "Title")
        content = form_get('content')
        check_empty(content, "Content")
        time = datetime.now()

    # TODO: flashed_message()
        if get_flashed_message():
            return render_template('create_comment.html', has_errors=True)

        new_comment_record = EventComment(event_id=event_id, user_id=user.id,
            contents=content, time=time)
        db.session.add(new_comment_record)
        db.session.commit()
        # TODO: decide how to show the comments
        return redirect(url_for('event_view',event_id=event_id))


@app.route('/event/comment/remove/<int:comment_id>', methods=['POST'])
@login_required
def comment_remove(comment_id):
    comment = EventComment.query.filter_by(id=comment_id, user_id=g.user.id)

    if comment is None:
        abort(403)
    else:
        event_id=comment.event_id
        comment.delete()
        db.session.commit()
        # TODO: check syntax of the line below
        return redirect(url_for('event_view',event_id=event_id))
