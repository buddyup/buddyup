from calendar import day_name

from flask import (request, session, flash, g, redirect, url_for, abort,
                   get_flashed_messages)


from buddyup.app import app
from buddyup.database import (User, Availability, Location, Course,
                              CourseMembership, Major, db)
from buddyup.util import form_get, login_required, check_empty
from buddyup.templating import render_template


@app.route('/setup/profile', methods=['POST', 'GET'])
@login_required
def profile_create():
    if request.method == 'GET':
        locations = Location.query.all()
        courses = Course.query.all()
        majors = Major.query.all()
        return render_template('setup/landing.html',
                               day_names=day_name,
                               locations=locations,
                               courses=courses,
                               selected=lambda record: False,
                               majors=majors,
                               )
    else:
        user = g.user
        name = form_get('name')
        check_empty(name, "Full Name")
        # Note: -1 is a marker for an empty location
        location = form_get('location', convert=int)

        if location != -1 and Location.query.get(location) is None:
            app.logger.info("Invalid location %s", location)
            abort(400)
        bio = form_get('bio')
        facebook = form_get('facebook')
        twitter = form_get('twitter')
        
        # If anything has been flashed, there was an error
        if get_flashed_messages():
            course_ids = set(request.form.getlist('course'))
            major_ids = set(request.form.getlist('majors'))
            # Define the appropriate selected() function
            def selected(record):
                if isinstance(record, Course):
                    return unicode(record.id) in course_ids
                elif isinstance(record, Location):
                    return unicode(record.id) == location
                elif isinstance(record, Major):
                    return unicode(record.id) in major_ids
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
                                   majors=Major.query.all()
                                   )

        user.full_name = name
        if location == -1:
            user.location_id = None
        else:
            user.location_id = location
        user.bio = bio
        user.initialized = True
        user.facebook = facebook
        user.twitter = twitter
        for major_id_text in request.form.getlist('majors'):
            try:
                major_id = int(major_id_text)
            except ValueError:
                app.logger.warning("non-integer major id %r sent by client",
                                   major_id_text)
                continue
            major_record = Major.query.get(major_id)
            if major_record is None:
                app.logger.warning("Non-existent major id %i sent by client",
                                   major_id_text)
                continue
            user.majors.append(major_record)
            
            
        
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

        return redirect(url_for('suggestions'))


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
        course_ids = {course.id for course in user.courses}
        def selected(record):
            if isinstance(record, Location):
                return user.location_id == record.id
            elif isinstance(record, Course):
                return record.id in course_ids
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
        check_empty(name, "Full Name")
        # Note: -1 is a marker for an empty location
        location = form_get('location', convert=int)
        if location != -1 and Location.query.get(location) is None:
            app.logger.info("Invalid location %s", location)
            abort(400)
        bio = form_get('bio')
        facebook = form_get('facebook')
        twitter = form_get('twitter')
        
        # If anything has been flashed, there was an error
        if get_flashed_messages():
            # Define the appropriate selected() function
            course_ids = set(map(int, request.form.getlist('course')))
            def selected(record):
                if isinstance(record, Course):
                    return record.id in course_ids
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
        if location == -1:
            user.location_id = None
        else:
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
