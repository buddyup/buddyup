from flask import g, request, abort, redirect, url_for

from buddyup.app import app
from buddyup.database import db, User, Notification
from buddyup.templating import render_template
from buddyup.util import login_required


@app.route('/notifications/')
@login_required
def list_notifications():
    notifications = Notification.query.filter(Notification.recipient_id==g.user.id).filter(Notification.deleted!=True)
    return render_template('notifications/list.html', notifications=notifications, user=g.user)


@app.route('/notifications/<int:id>', methods=['POST'])
@login_required
def clear_notification(id):
    notification = Notification.query.get_or_404(id)

    # YOU MUST OWN THIS NOTIFICATION.
    if notification.recipient != g.user:
        abort(404)

    db.session.delete(notification)
    db.session.commit()

    return "{}"


@app.route('/notifications/clear-all')
@login_required
def clear_notifications():
    for n in g.user.notifications:
        db.session.delete(n)
        db.session.commit()

    return redirect(url_for('list_notifications'))
