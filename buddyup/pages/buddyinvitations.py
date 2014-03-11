from operator import attrgetter

from flask import g, flash, redirect, url_for, abort, request
import mandrill

from buddyup.app import app
from buddyup.database import db, BuddyInvitation, User, EventInvitation
from buddyup.templating import render_template
from buddyup.util import (login_required, events_to_json, email,
                          send_mandrill_email_message, get_domain_name)


@app.route("/group")
@login_required
def group():
    events = []
    join_clubs = []
    event_invitations = (g.user.received_event_inv
                        .filter(EventInvitation.event_id != None)
                        .all())
    invited_unsorted = {}
    for inv in event_invitations:
        invited_unsorted.setdefault(inv.event, inv.sender)
    # list of (event, buddy) pairs
    invited = sorted(invited_unsorted.items(), reverse=True,
                     key=lambda v: v[0].start)
    for course in g.user.courses.all():
        events.extend(course.events)
    event_json = events_to_json(events)
    return render_template('my/view_invite.html',
                           events_json=event_json,
                           invited=invited)


@app.route("/invite/view")
@login_required
def invite_list():
    event_invitations = (g.user.received_event_inv
                         .filter(EventInvitation.event_id != None)
                         .all())
    buddy_invitations = g.user.received_bud_inv
    return render_template('my/invitation.html',
                           buddy_invitations=buddy_invitations,
                           event_invitations=event_invitations)


@app.route("/invite/send/<user_name>")
@login_required
def invite_send(user_name):
    if (user_name == g.user.user_name):
        abort(403)
    other_user_record = User.query.filter_by(user_name=user_name).first_or_404()
    other_id = other_user_record.id
    # already a friend
    if g.user.buddies.filter_by(id=other_id).count() == 1:
        flash("Already added!")
    # Other user sent an invite, accept
    elif (BuddyInvitation.query.filter_by(sender_id=other_id,
                                          receiver_id=g.user.id).count() == 1):
        g.user.buddies.append(other_user_record)
        other_user_record.buddies.append(g.user)
        flash("Accepted pending invitation")
    # Already sent an invitation
    elif (BuddyInvitation.query.filter_by(sender_id=g.user.id,
                                          receiver_id=other_id).count() == 1):
        flash("Invitation already pending")
    # No problems, send the invitation
    else:
        invite_record = BuddyInvitation(sender_id=g.user.id,
                            receiver_id=other_user_record.id)
        db.session.add(invite_record)
        db.session.commit()
        flash("Sent invitation to " + user_name)
        domain_name = get_domain_name()
        sbj = '%s wants to be your buddy on Buddyup' % email(g.user)
        msg = """<p>
                You have received a buddy request on BuddyUp.
                Click this link to accept the invitation: %s
                or this link to decline: %s
                </p>""" %\
              (domain_name + url_for('invite_accept', inv_id=invite_record.id),
               domain_name + url_for('invite_deny', inv_id=invite_record.id))
        send_mandrill_email_message(user_recipient=other_user_record,
                                    subject=sbj, html=msg)
    # TODO: Don't redirect to referrer (potential security risk?)
    # the 'or' picks referrer if its available, but uses buddy_view as a
    # fallback
    return redirect(request.referrer or url_for('buddy_view',
                                                user_name=user_name))


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
