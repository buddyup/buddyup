from flask import g, flash, redirect, url_for

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


@app.route("/invite/send/<user_name>", methods=['POST'])
@login_required
def invite_send(user_name):
    other_user_record = User.query.filter(user_name==user_name).first_or_404()
    invite_record = BuddyInvitation(sender_id=g.user.id,
                               receiver_id=other_user_record.id)
    db.session.add(invite_record)
    db.session.commit()
    flash("Sent invitation to " + user_name)
    return redirect(url_for('invite_list'))


@app.route("/invite/deny/<user_name>", methods=['POST'])
@login_required
def invite_deny(user_name):
    other_user_record = User.query.filter(user_name==user_name).first_or_404()
    invite_record = BuddyInvitation.query.filter_by(receiver_id=other_user_record.id).first_or_404()
    invite_record.delete()
    db.session.commit()
    flash("Ignored invitation from " + user_name)
    return render_template("invite/list.html",
                           other_user=other_user_record)


@app.route("/invite/accept/<user_name>", methods=['POST'])
@login_required
def invite_accept(user_name):
    other_user_record = User.query.filter(user_name==user_name).first_or_404()
    invite_record = BuddyInvitation.query.filter_by(receiver_id=other_user_record.id).first_or_404()
    invite_record.delete()
    # Us -> Them record
    buddy1_record = Buddy(user1_id=g.user.id, user2_id=other_user_record.id)
    db.session.add(buddy1_record)
    # Them -> Us record
    buddy2_record = Buddy(user2_id=g.user.id, user1_id=other_user_record.id)
    db.sesion.add(buddy2_record)
    db.session.commit()
    flash("Accepted invitation from " + user_name)
    return render_template("invite/list.html",
                           other_user=other_user_record)
