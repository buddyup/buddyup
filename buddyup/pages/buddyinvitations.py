from operator import attrgetter

from flask import g, flash, redirect, url_for, abort, request
import mandrill

from buddyup.app import app
from buddyup.database import db, BuddyInvitation, User, EventInvitation, Notification
from buddyup.templating import render_template
from buddyup.util import (login_required, email, send_email, acting_on_self)


"""
Buddy invitations are sent from one user to another. When you invite someone, you POST it under
their account. For example, jdoe wants to BuddyUp with jsmith. She'd POST to:

    /classmates/jsmith/invitation

When you respond to an invitation, you POST it to the inviting user's name under *your* own
invitations. So jsmith would reply with a POST to:

    /classmates/jsmith/invitations/jdoe

(Anyone else who tries to view that endpoint will see a 404.)

The value POSTed to that endpoint determines whether you're accepting or rejecting the invite.
"""


def already_invited(classmate):
    return BuddyInvitation.query.filter_by(sender_id=g.user.id, receiver_id=classmate.id, rejected=False).count() > 0

def they_invited_you(classmate):
    return BuddyInvitation.query.filter_by(sender_id=classmate.id, receiver_id=g.user.id).count() > 0


def already_buddy(classmate):
    return g.user.buddies.filter_by(id=classmate.id).count() > 0


def buddy_up(user1, user2):
        user1.buddies.append(user2)
        user2.buddies.append(user1)
        db.session.commit()


def email_invitation(from_user, to_user):

    invite_info = {
        'SENDER': from_user.full_name,
        'RECIPIENT': to_user.full_name,
        'DOMAIN': app.config.get('DOMAIN_NAME', ''),
    }

    subject = "%s wants to BuddyUp!" % invite_info['SENDER']

    message = """Hi {RECIPIENT}!

{SENDER} wants to be your buddy on BuddyUp.
View and respond to this invitation at: http://{DOMAIN}/notifications

Thanks,

The BuddyUp Team""".format(**invite_info)

    send_email(to_user, subject, message)

def email_accepted_invitation(from_user, to_user):

    invite_info = {
        'SENDER': from_user.full_name,
        'RECIPIENT': to_user.full_name,
        'DOMAIN': app.config.get('DOMAIN_NAME', ''),
    }

    subject = "%s accepted your invite!" % invite_info['RECIPIENT']

    message = """Hi {SENDER}!

{RECIPIENT} accepted your buddy invite - you're buddied up!

Thanks,

The BuddyUp Team
http://{DOMAIN}/""".format(**invite_info)

    send_email(from_user, subject, message)

def invite(sender, classmate):
    # Don't send multiple invitations.
    if BuddyInvitation.query.filter(BuddyInvitation.sender_id==sender.id, BuddyInvitation.receiver_id==classmate.id).count():
        return

    invitation = BuddyInvitation(sender_id=sender.id, receiver_id=classmate.id)
    db.session.add(invitation)
    db.session.commit()

    notification = Notification(sender_id=sender.id, recipient_id=classmate.id)

    notification.payload = "%s wants to BuddyUp!" % sender.full_name
    notification.action_text = "Accept"
    notification.action_link = "/classmates/%s/invitations/%s" % (classmate.user_name, sender.user_name)

    db.session.add(notification)
    db.session.commit()

    email_invitation(sender, classmate)


@app.route("/classmates/<user_name>/invitation", methods=["POST"])
@login_required
def invite_send(user_name):
    classmate = User.query.filter_by(user_name=user_name).first_or_404()

    if acting_on_self(classmate) or already_invited(classmate) or already_buddy(classmate):
        return redirect(request.referrer) # Just fall through. The UI shouldn't allow these.

    if they_invited_you(classmate):
        buddy_up(g.user, classmate)
        flash("You are now buddies!")
    else:
        invite(g.user, classmate)
        flash("Buddy invitation sent to " + classmate.full_name)

    return redirect(request.referrer)

def clear_buddy_invites(sender_id, receiver_id):
    BuddyInvitation.query.filter(BuddyInvitation.sender_id==sender_id, BuddyInvitation.receiver_id==receiver_id).delete()
    db.session.commit()


@app.route("/classmates/<receiver_name>/invitations/<sender_name>", methods=["POST"])
@login_required
def accept_invitation(receiver_name, sender_name):
    receiver = User.query.filter_by(user_name=receiver_name).first_or_404()
    sender = User.query.filter_by(user_name=sender_name).first_or_404()

    # This method only can be used from the receiver's view.
    # If we're not the receiver we see nothing.
    if not acting_on_self(receiver): abort(404)

    buddy_up(sender, receiver)
    clear_buddy_invites(sender.id, receiver.id)
    email_accepted_invitation(sender, receiver)

    # Once we've accepted the invitation, go visit the sender's page.
    return redirect(url_for('buddy_view', user_name=sender_name))
