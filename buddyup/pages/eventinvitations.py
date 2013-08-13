from flask import g, request, flash, direct, url_for, session, abort
from datetime import datetime

from buddyup.app import app
from buddup.database import User, EventInvitation, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get

@app.route('/buddy/invite/<int:event_id>/<user_name>', methods=['GET', 'POST'])
@login_required
def invite_to_event(event_id, user_name):
    if request.method == 'GET':
        return render_template('invite_event.html', event_id=event_id,
                user_name=user_name)
    else:
        sender = g.user
        receiver = User.query.filter_by(User.user_name==user_name).first_or_404()
        Event.query.get_or_404(event_id)
        new_invitation_record = EventInvitation(sender_id=sender.id,
                receiver_id=receiver.id, event_id=event_id)
        db.session.add(new_invitation_record)
        #TODO: check syntax
        db.session.commit() 
