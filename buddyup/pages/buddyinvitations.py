from flask import g, flash, redirect, url_for, abort, request

from buddyup.app import app
from buddyup.database import db, BuddyInvitation, User, Buddy
from buddyup.templating import render_template
from buddyup.util import login_required
from buddyup.pages.eventinvitations import event_invitation_view_all


@app.route("/invite/view")
@login_required
def invite_list():
    event_invitations = event_invitation_view_all()
    #for buddy_invitation in buddy_invitations:
    #    user = User.query.join(BuddyInvitation,User.id == BuddyInvitation.sender_id).filter_by(BuddyInvitation.id=buddy_invitation.id).first()
    buddy_invitations = g.user.received_bud_inv
    return render_template('my/view_invite.html',
                           buddy_invitations=buddy_invitations,
                           event_invitations=event_invitations)


@app.route("/invite/send/<user_name>")
@login_required
def invite_send(user_name):
    if (user_name == g.user.user_name):
        abort(403)
    other_user_record = User.query.filter_by(user_name=user_name).first_or_404()
    if ((g.user.buddies.filter_by(id=other_user_record.id).count() == 0) or
        (other_user_record.buddies.filter_by(id=g.user.id).count() == 0)):
        if not other_user_record.sent_bud_inv:
            invite_record = BuddyInvitation(sender_id=g.user.id,
                                receiver_id=other_user_record.id)
            db.session.add(invite_record)
            db.session.commit()
            flash("Sent invitation to " + user_name)
            return redirect(url_for('invite_list'))
        else:
            flash("Your invitation is pending")
            # TODO: Don't redirect to the referrer (security threat)
            return redirect(request.referrer)
    else:
        flash("Already added!")
        # TODO: Don't redirect to the referrer (security threat)
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
