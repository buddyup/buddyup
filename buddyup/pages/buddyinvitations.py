from operator import attrgetter

from flask import g, flash, redirect, url_for, abort, request
import mandrill

from buddyup.app import app
from buddyup.database import db, BuddyInvitation, User, EventInvitation
from buddyup.templating import render_template
from buddyup.util import (login_required, email, send_mandrill_email_message, get_domain_name, acting_on_self)


@app.route("/invite/view")
@login_required
def invite_list():
    event_invitations = (g.user.event_invitations_received
                         .filter(EventInvitation.event_id != None)
                         .all())
    buddy_invitations = g.user.buddy_invitations_received
    return render_template('my/invitation.html',
                           buddy_invitations=buddy_invitations,
                           event_invitations=event_invitations)


def compose_invitation_message(invite):
    sender = User.query.get(invite.sender_id)
    accept_link = get_domain_name() + url_for('invite_accept', inv_id=invite.id)
    decline_link = get_domain_name() + url_for('invite_deny', inv_id=invite.id)
    return """<p>
                You have received a buddy request from %s on BuddyUp.
                Click this link to accept the invitation: %s
                or this link to decline: %s
                </p>""" %\
                (sender.full_name, accept_link, decline_link)


def already_invited(classmate):
    return BuddyInvitation.query.filter_by(sender_id=g.user.id, receiver_id=classmate.id, rejected=False).count() > 0

def already_buddy(classmate):
    return g.user.buddies.filter_by(id=classmate.id).count() > 0

@app.route("/classmates/<user_name>/invitation", methods=["POST"])
@login_required
def invite_send(user_name):
    classmate = User.query.filter_by(user_name=user_name).first_or_404()

    if acting_on_self(classmate) or already_invited(classmate) or already_buddy(classmate):
        return redirect(request.referrer) # Just fall through. The UI shouldn't allow these.

    # Other user sent an invite, accept
    if (BuddyInvitation.query.filter_by(sender_id=classmate.id, receiver_id=g.user.id).count() > 0):
        g.user.buddies.append(classmate)
        classmate.buddies.append(g.user)
        flash("You are now buddies!")
    else:
        # Otherwise, send the invitation
        invitation = BuddyInvitation(sender_id=g.user.id, receiver_id=classmate.id)
        db.session.add(invitation)
        db.session.commit()
        flash("Sent invitation to " + classmate.full_name)

        sbj = '%s wants to be your buddy on Buddyup' % g.user.full_name
        msg = compose_invitation_message(invitation)

        send_mandrill_email_message(user_recipient=classmate, subject=sbj, html=msg)

    return redirect(request.referrer)


@app.route("/invite/deny/<int:inv_id>")
@login_required
def invite_deny(inv_id):
    inv_record = BuddyInvitation.query.get_or_404(inv_id)
    name = inv_record.sender.full_name
    db.session.delete(inv_record)
    db.session.commit()
    flash("Ignored invitation from " + name)
    return redirect(url_for('invite_list'))


@app.route("/invite/accept/<int:inv_id>")
@login_required
def invite_accept(inv_id):
    inv_record = BuddyInvitation.query.get_or_404(inv_id)
    receiver = g.user
    sender = inv_record.sender
    # Sender -> Receiver record
    if receiver.buddies.filter_by(id=sender.id).count() == 0:
        sender.buddies.append(receiver)
    # Receiver -> Sender
    if sender.buddies.filter_by(id=receiver.id).count() == 0:
        receiver.buddies.append(sender)
    db.session.delete(inv_record)
    db.session.commit()
    flash("Accepted invitation from " + sender.full_name)
    return redirect(url_for('invite_list'))
