from flask import request, session, flash

from buddyup.app import app
from buddyup.database import User, Availability, db
from buddyup.util import form_get
from buddyup.templating import render_template


@app.route('/profile/create/info', methods=['POST', 'GET'])
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
        last_name = form_get('last_name')
        if last_name == '':
            flash("Last Name Is Empty")
            error = True
        bio = form_get('bio')
        
        if error:
            return render_template("create_profile.html")

        user.first_name = first_name
        user.last_name = last_name
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


@app.route('/profile/create/photo', methods=['POST', 'GET'])
def create_photo():
    pass
    

@app.route('/my/profile/edit', methods=['POST', 'GET'])
def edit_profile():
    if request.method == 'POST':
        first_name = form_get('firstname')
        last_name = form_get('lastname')
        bio = form_get('bio')


@app.route('/my/profile/picture')
def change_picture():
    pass


@app.route('/my/availability', methods=['POST', 'GET'])
def edit_availability():
    pass
