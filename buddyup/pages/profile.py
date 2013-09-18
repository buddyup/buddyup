from calendar import day_name

from flask import (request, g, redirect, url_for, abort,
                   get_flashed_messages)
from buddyup.app import app
from buddyup.database import (Availability, Location, Course,
                              Major, Language, db)
from buddyup.util import (form_get, login_required, check_empty,
                          sorted_languages)
from buddyup.templating import render_template


# TODO: Rewrite profile_create with WTForms



def update_relationship(ids, relationship, model):
    """
    Use set manipulation to update a relationship using simple ids. Would
    be faster to directly use table manipulation, but we get a few extra
    nicities here.
    """
    current_ids = {record.id for record in relationship.all()}
    
    # Build a 
    new_ids = set()
    for id in ids:
        try:
            new_ids.add(int(id))
        except ValueError:
            app.logger.warning("Ignoring invalid id value %r for model %s",
                               id, model.__class__.__name__)

    insert_ids = new_ids - current_ids
    for id in insert_ids:
        record = model.query.get(id)
        if record is None:
            app.logger.warning("No record for id %i for model %s",
                               id, model.__class__.__name__)
        else:
            relationship.append(record)

    remove_ids = current_ids - new_ids
    for id in remove_ids:
        record = model.query.get(id)
        if record is None:
            app.logger.warning("No record for id %i for model %s",
                               id, model.__class__.__name__)
        else:
            relationship.append(record)


@app.route('/setup/profile', methods=['POST', 'GET'])
@login_required
def profile_create():
    if request.method == 'GET':
        locations = Location.query.all()
        courses = Course.query.all()
        majors = Major.query.all()
        languages = sorted_languages()
        def selected(record):
            if isinstance(record, Language):
                return record.name == u"English"
            else:
                return False
        return render_template('setup/landing.html',
                               day_names=day_name,
                               locations=locations,
                               courses=courses,
                               selected=selected,
                               majors=majors,
                               languages=languages,
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
            language_ids = set(request.form.getlist('languages'))
            # Define the appropriate selected() function
            def selected(record):
                if isinstance(record, Course):
                    return unicode(record.id) in course_ids
                elif isinstance(record, Location):
                    return unicode(record.id) == location
                elif isinstance(record, Major):
                    return unicode(record.id) in major_ids
                elif isinstance(record, Language):
                    return unicode(record.id) in language_ids
                else:
                    raise TypeError("Incorrect type %s" %
                                    record.__class__.__name__)
            return render_template('setup/landing.html',
                name=name,
                bio=bio,
                day_names=day_name,
                selected=selected,
                facebook=facebook,
                twitter=twitter,
                courses=Course.query.order_by('name').all(),
                locations=Location.query.order_by('name').all(),
                majors=Major.query.order_by('name').all(),
                languages=sorted_languages(),
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
                                   major_id)
                continue
            user.majors.append(major_record)
        for language_id_text in request.form.getlist('languages'):
            try:
                language_id = int(language_id_text)
            except ValueError:
                app.logger.warning("non-integer language id %r sent by client",
                                   language_id_text)
                continue
            language_record = Language.query.get(language_id)
            if language_record is None:
                app.logger.warning("Non-existent language id %i sent by client",
                                   language_id)
                continue
            user.languages.append(language_record)
            
        
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
            if day_lower not in request.form:
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
        update_relationship(request.form.getlist('course'), g.user.courses, Course)
        update_relationship(request.form.getlist('language'),
                            g.user.languages, Language)
        db.session.commit()

        return redirect(url_for('suggestions'))


# @app.route('/setup/photo', methods=['POST', 'GET'])
# @login_required
# def photo_create():
#    pass



@app.route('/user/profile', methods=['POST', 'GET'])
@login_required
def profile_edit():
    user = g.user
    if request.method == 'GET':
        course_ids = {course.id for course in user.courses}
        major_ids = {major.id for major in user.majors}
        def selected(record):
            if isinstance(record, Location):
                return user.location_id == record.id
            elif isinstance(record, Course):
                return record.id in course_ids
            elif isinstance(record, Major):
                return record.id in major_ids
            else:
                raise TypeError
        locations = Location.query.order_by('name').all()
        courses = Course.query.order_by('name').all()
        majors = Major.query.order_by('name').all()
        languages = sorted_languages()
        return render_template('my/edit_profile.html',
                               day_names=day_name,
                               locations=locations,
                               courses=courses,
                               selected=selected,
                               majors=majors,
                               languages=languages,
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
            course_ids = set(request.form.getlist('course'))
            major_ids = set(request.form.getlist('major'))
            def selected(record):
                if isinstance(record, Course):
                    return unicode(record.id) in course_ids
                elif isinstance(record, Location):
                    return record.id == location
                elif isinstance(record, Major):
                    return unicode(record.id) in major_ids
                else:
                    raise TypeError("Incorrect type %s" %
                                    record.__class__.__name__)
            locations = Location.query.order_by('name').all()
            majors = Major.query.order_by('name').all()
            return render_template('my/edit_profile.html',
                                   locations=locations,
                                   majors=majors,
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

        course_ids = map(int, request.form.getlist('course'))
        update_relationship(course_ids, g.user.courses, Course)
        language_ids = map(int, request.form.getlist('languages'))
        update_relationship(language_ids, g.user.languages, Language)
        db.session.commit()
        return redirect(url_for('buddy_view', user_name=g.user.user_name))

@app.route('/my/profile/picture')
@login_required
def photo_change():
    pass
