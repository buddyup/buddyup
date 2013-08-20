from flask import g, request, flash, redirect, url_for, session, abort
from datetime import datetime

from buddyup.app import app
from buddyup.database import User, EventInvitation, EventMembership, db, Event
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get

@login_required
def event_invitation_view_all():
    event_invitations = EventInvitation.query.filter_by(receiver_id=g.user.id)
    return event_invitations

@app.route('/invite/event/<int:event_id>/<user_name>', methods=['GET', 'POST'])
@login_required
def invite_to_event(event_id, user_name):
    event_invitation_send(event_id, user_name)


@login_required
def event_invitation_send(event_id, user_name):
    Event.query.get_or_404(event_id)
    receiver = User.query.filter_by(user_name==user_name).first_or_404()
    
    if EventMembership.query.filter_by(event_id=event_id,
            user_id=receiver.id) is None:
        if EventInvitation.query.filter_by(sender_id=g.user.id,
                receiver_id=receiver.id).first() is None:
            new_invitation_record = EventInvitation(sender_id=g.user.id,
                    receiver_id=receiver.id, event_id=event_id)
            db.session.add(new_invitation_record)
            db.session.commit()

    else:
        #TODO: SAYING THAT USER IS ALREADY IN!
        pass


@app.route('/accept/event/<int:invitation_id>', methods=['POST'])
def event_invitation_accept(invitation_id):
    if request.method == 'GET':
        abort(403)

    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    if EventMembership.query.filter_by(event_id=event_invitation.event_id,
            user_id=event_invitation.user_id).first() is None:
        new_attendance_record = EventMembership(event_id=event_invitation.event_id,
                user_id=event_invitation.user_id)
        db.session.add(new_attendance_record)
        db.session.delete(event_invitation)
        db.session.commit()
        #TODO: NOT SURE WHAT'S NEXT!
        pass

    else:
        #TODO: SAYING HES ALREADY IN!
        pass

@app.route('/decline/event/<int:invitation_id>', methods=['POST'])
def event_invitation_decline(invitation_id):
    if request.method == 'GET':
        abort(403)

    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    event_invitation.delete()
    db.session.commit()

