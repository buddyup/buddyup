from flask import url_for

from buddyup import database


def url_for_user(user, **kwargs):
    return _url_for_profile(user, 'user_view', database.User, kwargs)


def url_for_group(group, **kwargs):
    return _url_for_profile(group, 'group_view', database.Group, kwargs)


def url_for_event(event, **kwargs):
    return _url_for_profile(event, 'event_view', database.Event, kwargs)


def url_for_course(course, **kwargs):
    return _url_for_profile(course, 'course_view', database.Course, kwargs)


def _url_for_profile(id, base, kls, kwargs):
    # base: url_for(base)
    # profile_id: id number or instance of kls
    # kls: Viewable profile from buddyup.database
    # returns str
    if isinstance(id, kls):
        id = id.id
    return "%s/profile/%i" % (url_for(base), id)
