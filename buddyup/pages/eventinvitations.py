from flask import g, request, flash, redirect, url_for, abort

from enum import Enum

from buddyup.app import app
from buddyup.database import User, EventInvitation, EventMembership, db, Event, Course
from buddyup.util import login_required, send_mandrill_email_message, get_domain_name
from buddyup.templating import render_template


class InvitationResult(Enum):
    success = 1
    already_sent = 2
    already_in_group = 3


@app.route('/invite/event/<int:event_id>', methods = ['GET', 'POST'])
@login_required
def event_invitation_send_list(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Only attendances have the permission to invite to the event
    if not g.user.events.filter_by(id=event_id).count():
        abort(403)


    if request.method == 'GET':
        return render_template('group/invite.html',
                               event=event,
                               buddies=g.user.buddies)
    else:
        if 'invite_classmates' in request.form:
            users = event.course.users.filter(User.id != g.user.id).all()
        else:
            users = []
            user_ids = map(int, request.form.getlist('users'))
            for user_id in user_ids:
                # Skip users that don't exist to prevent race conditions
                user = User.query.get(user_id)
                if user is not None:
                    users.append(user)
                
        for user in users:
            # All statuses are fine
            _send_invitation(event, user)
        return redirect(url_for('event_view', event_id=event_id))


@app.route('/invite/event/<int:event_id>/<user_name>', methods=['GET', 'POST'])
@login_required
def event_invitation_send(event_id, user_name):
    if (user_name == g.user.user_name):
        abort(403)
    user = User.query.filter_by(user_name=user_name).first_or_404()
    
    event = Event.query.get_or_404(event_id)
    status = _send_invitation(event, user)
    flash({
        InvitationResult.success: "Invited {} to group" % user.full_name,
        InvitationResult.already_in_group: "Already in group",
        InvitationResult.already_sent: "Invitation already sent",
        }[status])
    return redirect(request.referrer)


def _send_invitation(event, user):
    # Already in group?
    already_in_group = (db.session.query(EventMembership)
                        .filter_by(event_id=event.id, user_id=user.id)
                        .count() > 0)
    if already_in_group:
        return InvitationResult.already_member
    # Already invited?
    already_sent = (EventInvitation.query
                    .filter_by(event_id=event.id, receiver_id=user.id)
                    .count() > 0)
    if already_sent:
        return InvitationResult.already_sent
    
    
    new_invitation_record = EventInvitation(sender_id=g.user.id,
            receiver_id=user.id, event_id=event.id)
    db.session.add(new_invitation_record)
    db.session.flush()
    db.session.refresh(new_invitation_record)
    invitation_id = new_invitation_record.id
    sbj = "You've been invited to a group on Buddyup"
    domain_name = get_domain_name()
    msg = """<p>
                You've been invited to a buddyup group.
                Click this link to accept the invitation: %s
                or this link to decline: %s
            </p>""" %\
            (domain_name + url_for('event_invitation_accept', invitation_id=invitation_id),
            domain_name + url_for('event_invitation_decline', invitation_id=invitation_id)),
    send_mandrill_email_message(user_recipient=user, subject=sbj, html=msg)
    app.logger.info("Sent invitation for event #%d to %s",
                    event.id, user.user_name)
    return InvitationResult.success


@app.route('/accept/event/<int:invitation_id>')
def event_invitation_accept(invitation_id):
    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    event = Event.query.get_or_404(event_invitation.event_id)
    if not g.user.events.filter_by(id=event.id).count():
        g.user.events.append(event)
        db.session.delete(event_invitation)
        db.session.commit()
        flash("The new event has been successfully added.")
    else:
        flash("This event has already been added.")

    return redirect(url_for('invite_list'))


@app.route('/decline/event/<int:invitation_id>')
def event_invitation_decline(invitation_id):
    event_invitation = EventInvitation.query.get_or_404(invitation_id)
    event_invitation.delete()
    db.session.commit()
    return redirect(url_for('invite_list'))

