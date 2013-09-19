from flask import (g, request, redirect, url_for, session, abort,
                   get_flashed_messages)
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Event, EventComment, Course, EventMembership, db
from buddyup.templating import render_template
from buddyup.util import login_required, form_get, check_empty
from buddyup.pages.events import event_view


@app.route('/event/comment/create/<int:event_id>', methods=['POST'])
@login_required
def post_comment(event_id):
    Event.query.get_or_404(event_id)
    content = form_get('content')
    check_empty(content, "Content")
    time = datetime.now()

    comment_record = EventComment(event_id=event_id, user_id=g.user.id,
        contents=content, time=time)
    db.session.add(comment_record)
    db.session.commit()
    # TODO: decide how to show the comments
    return redirect(url_for('event_view', event_id=event_id))


@app.route('/event/comment/edit/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_edit(comment_id):
    comment = EventComment.query.filter(id=comment_id, user_id=g.user.id).first_or_404()
    
    if request.method == 'GET':
        return render_template('/group/edit_comment.html', comment = comment)
    else:
        contents = form_get('contents')
        check_empty(contents, "Contents")
        if get_flashed_messages():
            return render_template('/group/edit_comment.html',
                    comment = comment)
        comment.contents=contents
        comment.time = datetime.now()
        db.session.commit()
        return redirect(url_for('event_view', event_id = comment.event_id))


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
        return redirect(url_for('event_view',event_id=event_id))
