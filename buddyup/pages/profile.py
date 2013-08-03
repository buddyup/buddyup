from flask import request, session, flash, g, redirect, url_for

from buddyup.app import app
from buddyup.database import User, Availability, db
from buddyup.util import form_get
from buddyup.templating import render_template, login_required


@app.route('/user/create/info', methods=['POST', 'GET'])
@login_required
def create_profile():
    if request.method == 'GET':
        return render_template('create_profile.html')
    else:
        user = g.user
        error = False
        first_name = form_get('first_name')
        if first_name == '':
            flash("First Name Is Empty")
            error = True
        # Last name should be optional
        last_name = form_get('last_name')
        # TODO: enum gender
        gender = form_get('gender')
        location = form_get('location')
        bio = form_get('bio')
        
        if error:
            return render_template('create_profile.html')

        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.location = location
        user.bio = bio
        user.initialized = True
        db.update(user)
        
        for i in range(7):
            am_name = "{day}-am"
            if am_name in request.form:
                am_record = Availability(user_id=user.id,
                                         day=i,
                                         time='pm',
                                         available=pm_checked)
            db.add(am_record)
            pm_name = "{day}-pm"
            if pm_name in request.form:
                pm_record = Availability(user_id=user.id,
                                         day=i,
                                         time='pm',
                                         available=pm_checked)
            db.add(pm_record)
        db.commit()
        # TODO: figure out what's next and redirect to that page
#        return redirect(url_for(


@app.route('/user/create/photo', methods=['POST', 'GET'])
def create_photo():
    pass
    
@app.route('/user/profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    if request.method == 'POST':
        first_name = form_get('firstname')
        last_name = form_get('lastname')
        gender = form_get('gender')
        bio = form_get('bio')
        location = form_get('location')

        user = g.user
        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.bio = bio
        user.location = location
        db.update(user)

        # TODO: get availability and replace the old records

        db.commit()
        return redirect(url_for('edit_profile'))
    else:
        return render_template('view_profile.html', user=g.user)

@app.route('/my/profile/picture')
def change_picture():
    pass

# Will be combine with edit_profile
@app.route('/my/availability', methods=['POST', 'GET'])
def edit_availability():
    pass
