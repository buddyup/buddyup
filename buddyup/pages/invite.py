from flask import g

from buddyup.app import app
from buddyup.database import db, Invitation, User, Buddy
from buddyup.templating import render_template
from buddyup.util import login_required


@app.route("/invite/view")
@login_required
def view_invites():
    invitations = g.user.invitations.all()
    return render_template('invite/view.html',
                           invitations=invitations)


@app.route("/invite/send/<user_name>")
@login_required
def send_invite(user_name):
    other_user_record = User.query.filter(user_name=user_name).first_or_404()
    invite_record = Invitation(sender_id=g.user_record.id,
                               receiver_id=other_user_record.id)
    db.session.add(invite_record)
    db.session.commit()
    return render_template("invite/sent.html",
                           other_user=other_user_record)


@app.route("/invite/deny/<user_name>")
@login_required
def deny_invite(user_name):
    other_user_record = User.query.filter(user_name=user_name).first_or_404()
    invite_record = Invitation.query.filter(receiver_id=other_user_record.id).first_or_404()
    invite_record.delete()
    db.session.commit()
    return render_template("invite/denied.html",
                           other_user=other_user_record)


@app.route("/invite/accept/<user_name>")
@login_required
def accept_invite(user_name):
    other_user_record = User.query.filter(user_name=user_name).first_or_404()
    invite_record = Invitation.query.filter(receiver_id=other_user_record.id).first_or_404()
    invite_record.delete()
    # Us -> Them record
    buddy1_record = Buddy(user1_id=g.user.id, user2_id=other_user_record.id)
    db.add(buddy1_record)
    # Them -> Us record
    buddy2_record = Buddy(user2_id=g.user.id, user1_id=other_user_record.id)
    db.add(buddy2_record)
    db.commit()
    return render_template("invite/accepted.html",
                           other_user=other_user_record)
