from calendar import day_name

from flask import request, session, flash, g, redirect, url_for

from buddyup.app import app
from buddyup.database import User, Availability, Location, db
from buddyup.util import form_get, login_required
from buddyup.templating import render_template


@app.route('/setup/profile', methods=['POST', 'GET'])
@login_required
def profile_create():
    if request.method == 'GET':
        locations = Location.query.all()
        return render_template('setup/landing.html', locations=locations)
    else:
        user = g.user
        name = form_get('first_name')
        check_empty(first_name, "Full Name")
        location = form_get('location', convert=int)
        if Locations.query.get(location) is None:
            abort(400)
        bio = form_get('bio')
        
        # If anything has been flashed, there was an error
        if get_flashed_messages():
            return render_template('setup/landing.html', day_names=day_name)

        user.full_name = name
        user.location_id = location
        user.bio = bio
        user.initialized = True
        db.session.update(user)
        
        AVAILABILITIES = {
            'am': ('am',),
            'pm': ('pm',),
            'both': ('am', 'pm')
        }

        for i, day in enumerate(day_names):
            availability = form_get('availability-{}'.format(day))
            if availability not in AVAILABILITIES:
                abort(400)
            for time in AVAILABILITIES[availability]:
                record = Availability(user_id=user.id,
                                      day=i,
                                      time=time)
                db.add(record)
        db.session.commit()
        # TODO: figure out what's next and redirect to that page
        return redirect(url_for('home'))


# @app.route('/setup/photo', methods=['POST', 'GET'])
# @login_required
# def photo_create():
#    pass
    

@app.route('/user/profile', methods=['POST', 'GET'])
@login_required
def profile_edit():
    if request.method == 'POST':
        first_name = form_get('firstname')
        last_name = form_get('lastname')
        bio = form_get('bio')
        location = form_get('location')

        user = g.user
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.location = location
        db.update(user)

        # TODO: get availability and replace the old records

        db.commit()
        return redirect(url_for('profile_view', user_name=g.user.full_name))
    else:
        return render_template('profile/edit.html')


@app.route('/my/profile/picture')
@login_required
def photo_change():
    pass
