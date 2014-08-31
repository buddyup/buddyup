from operator import attrgetter

from flask import g, flash, redirect, url_for, abort, request
import mandrill

from buddyup.app import app
from buddyup.database import db, BuddyInvitation, User, EventInvitation, Notification
from buddyup.templating import render_template
from buddyup.util import (login_required, email, send_mandrill_email_message, get_domain_name, acting_on_self)


    # If I POST to an invitation under my account, that means I accept it.
    # If I POST to an invitation under someone else's account, that means I'm inviting them.





def already_invited(classmate):
    return BuddyInvitation.query.filter_by(sender_id=g.user.id, receiver_id=classmate.id, rejected=False).count() > 0

def they_invited_you(classmate):
    return BuddyInvitation.query.filter_by(sender_id=classmate.id, receiver_id=g.user.id).count() > 0


def already_buddy(classmate):
    return g.user.buddies.filter_by(id=classmate.id).count() > 0

def buddy_up(user1, user2):
        user1.buddies.append(user2)
        user2.buddies.append(user1)

@app.route("/classmates/<user_name>/invitation", methods=["POST"])
@login_required
def invite_send(user_name):

    classmate = User.query.filter_by(user_name=user_name).first_or_404()

    if acting_on_self(classmate) or already_invited(classmate) or already_buddy(classmate):
        return redirect(request.referrer) # Just fall through. The UI shouldn't allow these.

    if they_invited_you(classmate):
        # Other user already sent an invite. Go directly to buddies.
        buddy_up(g.user, classmate)
        flash("You are now buddies!")
    else:
        # Otherwise, send the invitation
        invitation = BuddyInvitation(sender_id=g.user.id, receiver_id=classmate.id)
        db.session.add(invitation)
        db.session.commit()

        notification = Notification(sender_id=g.user.id, recipient_id=classmate.id)

        notification.payload = "%s wants to BuddyUp!" % g.user.full_name
        notification.action_text = "Accept"
        notification.action_link = "/classmates/%s/invitation"

        db.session.add(notification)
        db.session.commit()

        flash("Sent invitation to " + classmate.full_name)

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
