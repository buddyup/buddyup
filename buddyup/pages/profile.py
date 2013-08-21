from calendar import day_name

from flask import (request, session, flash, g, redirect, url_for, abort,
                   get_flashed_messages)


from buddyup.app import app
from buddyup.database import (User, Availability, Location, Course,
                              CourseMembership, db)
from buddyup.util import form_get, login_required, check_empty
from buddyup.templating import render_template


@app.route('/setup/profile', methods=['POST', 'GET'])
@login_required
def profile_create():
    if request.method == 'GET':
        locations = Location.query.all()
        courses = Course.query.all()
        return render_template('setup/landing.html',
                               day_names=day_name,
                               locations=locations,
                               courses=courses,
                               selected=lambda record: False,
                               )
    else:
        user = g.user
        name = form_get('name')
        course = form_get('course', convert=int)
        check_empty(name, "Full Name")
        location = form_get('location', convert=int)
        if Location.query.get(location) is None:
            app.logger.info("Invalid location %s", location)
            abort(400)
        bio = form_get('bio')
        facebook = form_get('facebook')
        twitter = form_get('twitter')
        
        # If anything has been flashed, there was an error
        if get_flashed_messages():
            # Define the appropriate selected() function
            def selected(record):
                if isinstance(record, Course):
                    return record.id == course
                elif isinstance(record, Location):
                    return record.id == location
                else:
                    raise TypeError("Incorrect type %s" %
                                    record.__class__.__name__)
            locations = Location.query.all()
            return render_template('setup/landing.html',
                                   locations=locations,
                                   name=name,
                                   bio=bio,
                                   day_names=day_name,
                                   selected=selected,
                                   facebook=facebook,
                                   twitter=twitter,
                                   courses=Course.query.all(),
                                   )

        user.full_name = name
        user.location_id = location
        user.bio = bio
        user.initialized = True
        user.facebook = facebook
        user.twitter = twitter
        
        AVAILABILITIES = {
            'am': ('am',),
            'pm': ('pm',),
            'all': ('am', 'pm'),
            None: (),
        }

        for i, day in enumerate(day_name):
            day_lower = day.lower()
            availability = form_get('availability-{}'.format(day_lower), default=None)
            # Skip if the user unchecked the day's box
            if day.lower() not in request.form:
                continue
            # Error on invalid am/pm values
            if availability not in AVAILABILITIES:
                app.logger.info("Invalid availability %s", availability)
                abort(400)

            for time in AVAILABILITIES[availability]:
                record = Availability(user_id=user.id,
                                      day=i,
                                      time=time)
                db.add(record)
        update_courses(map(int, request.form.getlist('course')))
        db.session.commit()

        return redirect(url_for('welcome'))


# @app.route('/setup/photo', methods=['POST', 'GET'])
# @login_required
# def photo_create():
#    pass
 
def update_courses(course_ids):
    """
    Use set manipulation delete removed course links and insert new course
    links.
    """
    current_course_ids = {course.id for course in g.user.courses.all()}
    new_course_ids = set(course_ids)

    new = new_course_ids - current_course_ids
    for course_id in new:
        course = Course.query.get(course_id)
        g.user.courses.append(course)
    
    remove = current_course_ids - new_course_ids
    for course_id in remove:
        course = Course.query.get(course_id)
        g.user.courses.remove(course)


@app.route('/user/profile', methods=['POST', 'GET'])
@login_required
def profile_edit():
    user = g.user
    if request.method == 'GET':
        def selected(record):
            if isinstance(record, Location):
                return user.location_id == record.id
            elif isinstance(record, Course):
                return user.courses.filter_by(id=record.id).count() != 0
            else:
                raise TypeError
        locations = Location.query.all()
        courses = Course.query.all()
        return render_template('my/edit_profile.html',
                               day_names=day_name,
                               locations=locations,
                               courses=courses,
                               selected=selected,
                               )
    else:
        name = form_get('name')
        course = form_get('course', convert=int)
        check_empty(name, "Full Name")
        location = form_get('location', convert=int)
        if Location.query.get(location) is None:
            app.logger.info("Invalid location %s", location)
            abort(400)
        bio = form_get('bio')
        facebook = form_get('facebook')
        twitter = form_get('twitter')
        
        # If anything has been flashed, there was an error
        if get_flashed_messages():
            # Define the appropriate selected() function
            def selected(record):
                if isinstance(record, Course):
                    return record.id == course
                elif isinstance(record, Location):
                    return record.id == location
                else:
                    raise TypeError("Incorrect type %s" %
                                    record.__class__.__name__)
            locations = Location.query.all()
            return render_template('my/edit_profile.html',
                                   locations=locations,
                                   name=name,
                                   bio=bio,
                                   day_names=day_name,
                                   selected=selected,
                                   facebook=facebook,
                                   twitter=twitter
                                   )

        user.full_name = name
        user.location_id = location
        user.bio = bio
        user.initialized = True
        user.facebook = facebook
        user.twitter = twitter
        
        AVAILABILITIES = {
            'am': ('am',),
            'pm': ('pm',),
            'all': ('am', 'pm'),
            None: (),
        }

        for i, day in enumerate(day_name):
            day_lower = day.lower()
            availability = form_get('availability-{}'.format(day_lower), default=None)
            # Skip if the user unchecked the day's box
            if day.lower() not in request.form:
                continue
            # Error on invalid am/pm values
            if availability not in AVAILABILITIES:
                app.logger.info("Invalid availability %s", availability)
                abort(400)

            for time in AVAILABILITIES[availability]:
                record = Availability(user_id=user.id,
                                      day=i,
                                      time=time)
                db.add(record)

        update_courses(map(int, request.form.getlist('course')))
        db.session.commit()
        return redirect(url_for('buddy_view', user_name=g.user.user_name))

@app.route('/my/profile/picture')
@login_required
def photo_change():
    pass
