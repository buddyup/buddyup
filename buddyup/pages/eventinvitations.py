from flask import g, request, flash, redirect, url_for, abort

from buddyup.app import app
from buddyup.database import User, EventInvitation, EventMembership, db, Event, Course
from buddyup.util import login_required
from buddyup.templating import render_template


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
        user_ids = map(int, request.form.getlist('users'))
        invite_classmates = request.form.getlist('invite_classmates')
        if invite_classmates != []:
            event = Event.query.get_or_404(event_id)
            course_name = Course.query.get_or_404(event.course_id)
            curr_database = User.query.join(Course.users).filter(Course.name == course_name.name).all()
            for user in curr_database:
                if user.id in user_ids:
                    continue
                else:
                    user_ids.append(user.id)
        for user_id in user_ids:
            if user_id == g.user.id:
                continue
            else:
                user=User.query.get_or_404(user_id)
                event_invitation_send(event_id, user.user_name)
        return redirect(url_for('event_view', event_id=event_id))




@app.route('/invite/event/<int:event_id>/<user_name>', methods=['GET', 'POST'])
@login_required
def event_invitation_send(event_id, user_name):
    if (user_name == g.user.user_name):
        abort(403)
    
    Event.query.get_or_404(event_id)
    receiver = User.query.filter_by(user_name=user_name).first_or_404()
    
    if db.session.query(EventMembership).filter_by(event_id=event_id,
            user_id=receiver.id).count() == 0:
        if not EventInvitation.query.filter_by(sender_id=g.user.id,
                receiver_id=receiver.id).count():
            new_invitation_record = EventInvitation(sender_id=g.user.id,
                    receiver_id=receiver.id, event_id=event_id)
            db.session.add(new_invitation_record)
            db.session.commit()
        else:
            flash("Your invitation is pending")
            # TODO: Redirect to sender is ridiculously insecure. Find
            # another way!
            return redirect(request.referrer)
    else:
        flash("Already in!")
        return redirect(request.referrer)



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

