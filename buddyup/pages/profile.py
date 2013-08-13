from flask import request, session, flash, g, redirect, url_for

from buddyup.app import app
from buddyup.database import User, Availability, db
from buddyup.util import form_get, login_required, check_empty
from buddyup.templating import render_template


@app.route('/user/create/', methods=['POST', 'GET'])
@login_required
def create_profile_1():
    if request.method == 'GET':
        return render_template('landing.html', has_errors=False)
    else:
        user = g.user
        first_name = form_get('first_name')
        check_empty('first_name')
        # Last name is optional
        last_name = form_get('last_name')
        gender = form_get('gender')
        location = form_get('location')
        #bio = form_get('bio')
        
        if get_flashed_message():
            return render_template('landing.html', has_errors=True)

        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.location = location
        user.bio = bio
        user.initialized = True
        db.session.update(user)
        
        for i in range(7):
            am_name = "{day}-am"
            if am_name in request.form:
                am_record = Availability(user_id=user.id,
                                         day=i,
                                         time='pm',
                                         available=pm_checked)
            db.session.add(am_record)
            pm_name = "{day}-pm"
            if pm_name in request.form:
                pm_record = Availability(user_id=user.id,
                                         day=i,
                                         time='pm',
                                         available=pm_checked)
            db.session.add(pm_record)
        db.session.commit()
        # TODO: figure out what's next and redirect to that page
        return redirect(url_for('create_profile_2')


@app.route('/user/create/\#', methods=['GET', 'POST'])
@login_required
def create_profile_2():
    if method='GET':
        return render_template('landing2.html')
    else:
        #TODO: get picture
        facebook = form_get('facebook')
        email = form_get('email')
        note = form_get('note')
        user = g.user
        user.facebook = facebook
        user.email = email
        user.note = note
        db.session.update(user)
        db.session.commit()
        
        return redirect(url_for('home'))


@app.route('/user/create/photo', methods=['POST', 'GET'])
@login_required
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
@login_required
def change_photo():
    pass

# Will be combine with edit_profile
@app.route('/my/availability', methods=['POST', 'GET'])
def edit_availability():
    pass
