from flask import g, request, flash, redirect, url_for, session, abort

from buddyup.app import app
from buddyup.database import User, EventInvitation, EventMembership, db, Event
from buddyup.util import login_required
from buddyup.pages.buddyinvitations import invite_list

@login_required
def event_invitation_view_all():
    event_invitations = g.user.received_eve_inv
    return event_invitations

@app.route('/invite/event/<int:event_id>/<user_name>', methods=['GET', 'POST'])
@login_required
def event_invitation_send(event_id, user_name):
    if (user_name == g.user.user_name):
        abort(403)
    
    Event.query.get_or_404(event_id)
    receiver = User.query.filter_by(user_name==user_name).first_or_404()
    
    if EventMembership.query.filter_by(event_id=event_id,
            user_id=receiver.id) is None:
        if not EventInvitation.query.filter_by(sender_id=g.user.id,
                receiver_id=receiver.id):
            new_invitation_record = EventInvitation(sender_id=g.user.id,
                    receiver_id=receiver.id, event_id=event_id)
            db.session.add(new_invitation_record)
            db.session.commit()
        else:
            flash("Your invitation is pending")
            return redirect(request.referrer)
    else:
        flash("Already in!")
        return redirect(request.referrer)


@app.route('/accept/event/<int:invitation_id>', methods=['POST'])
def event_invitation_accept(invitation_id):
    if request.method == 'GET':
        abort(403)

    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    event = Event.query.get_or_404(event_invitation.event_id)
    if not g.user.events.filter_by(id=event.id):
        g.user.events.append(event)
        db.session.delete(event_invitation)
        db.session.commit()
        flash("The new event has been successfully added.")

    else:
        flash("This event has already been added.")

    return redirect(url_for('invite_list'))

@app.route('/decline/event/<int:invitation_id>', methods=['POST'])
def event_invitation_decline(invitation_id):
    if request.method == 'GET':
        abort(403)

    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    event_invitation.delete()
    db.session.commit()
    return redirect(url_for('invite_list'))

