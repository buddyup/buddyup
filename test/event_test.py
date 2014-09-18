import unittest
import json
from datetime import datetime, timedelta
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course, Event, EventInvitation, EventComment, Notification
from buddyup.util import time_from_timestamp
from bs4 import BeautifulSoup

class EventTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

        # Create demo Course
        course = Course(name="Basketweaving 451")
        db.session.add(course)
        db.session.commit()

        # Create a user profile to invite.
        skippy = User(user_name="skippy", full_name="Skippy Binks")
        skippy.initialized = True
        skippy.has_photos = True
        db.session.add(skippy)
        db.session.commit()

        # Create a user to run our tests as.
        test_user = User(user_name="test_user", full_name="John Smith")
        test_user.initialized = True
        test_user.has_photos = True
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])
        else:
            db.drop_all()


    # TODO: Make this NOT a property, it causes too much hassle w/ sqlalchemy sessions. Call once
    # and cache in your test method.
    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
        if login.status == '200 OK': return client


    @property
    def skippy_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=skippy', follow_redirects=True)
        if login.status == '200 OK': return client




    def test_timestamp_to_time(self):

        midnight = 0
        self.assertEqual("12:00AM", time_from_timestamp(midnight)[-1])

        noon = 43200
        self.assertEqual("12:00PM", time_from_timestamp(noon)[-1])

        nine_thirty_am = 34200
        self.assertEqual("9:30AM", time_from_timestamp(nine_thirty_am)[-1])

        elevent_thirty_pm = 86400 - 1800
        self.assertEqual("11:30PM", time_from_timestamp(elevent_thirty_pm)[-1])



    def test_json_for_events(self):

        course_id = Course.query.first().id

        result = self.test_client.get('/courses/1/events.json', follow_redirects=True)

        self.assertEqual(result.status_code, 200)

        result = json.loads(result.data)

        empty_result = {u'result': [], u'success': 1}

        # JSON should be empty before there are events.
        self.assertDictEqual(empty_result, result)

        # Now create our Event
        event = Event(course_id=course_id, name="Test Event")

        db.session.add(event)
        db.session.commit()

        result = self.test_client.get('/courses/1/events.json', follow_redirects=True)

        data = json.loads(result.data)

        self.assertEqual(len(data['result']), 1)

        # JSON should have a single Event afterwards.


    def test_create_event(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id
        url = '/courses/%s/event' % course_id

        self.assertEqual(0, Event.query.count(), "No events should exist yet.")

        new_event_page = client.get(url, follow_redirects=True)

        self.assertEqual('200 OK', new_event_page.status)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        response = client.post(url, data=new_event_request, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(1, Event.query.count())

        new_event = Event.query.first()

        self.assertEqual(course_id, new_event.course_id)

        self.assertEqual(user_id, new_event.owner_id)

        self.assertEqual("03:30PM", new_event.start.strftime("%I:%M%p"))

        self.assertEqual("05:00PM", new_event.end.strftime("%I:%M%p"))

        # Owner should automatically attend event.
        self.assertIn(new_event, User.query.filter(User.user_name=="test_user").first().events.all())



    def test_event_times(self):
        """
        Make sure the Start and End times are sane.
        """
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id
        url = '/courses/%s/event' % course_id

        new_event_page = client.get(url, follow_redirects=True)
        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "61200", # 5:00pm,
            "end": "55800", # 3:30pm
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        response = client.post(url, data=new_event_request, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(0, Event.query.count(), "That event should not have been created because the times are negative.")


    def test_invite_coursemate_to_event(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        course = Course.query.first()

        # We and skippy need to be coursemates.
        test_user.courses.append(course)
        skippy.courses.append(course)

        db.session.commit()

        create_event_url = '/courses/%s/event' % course.id

        new_event_page = client.get(create_event_url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        client.post(create_event_url, data=new_event_request, follow_redirects=True)

        # Event exists now. Let's invite Skippy.

        # Skippy shouldn't have an event yet.
        skippy_id = User.query.filter_by(user_name="skippy").first().id
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id).count()
        self.assertEqual(0, skippy_invite_count)

        self.assertEqual(0, Notification.query.count())

        new_event = Event.query.first()

        event_invite_url = '/courses/%s/events/%s/invitation' % (course.id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value']

        invitation = {
            'csrf_token': csrf_token,
            'everyone': "false",
            'invited': [skippy_id]
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        test_user_id = User.query.filter_by(user_name="test_user").first().id

        # Skippy should have his invite by now.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count()
        self.assertEqual(1, skippy_invite_count)

        # Skippy should have an invitation.
        self.assertEqual(1, Notification.query.count())


    def test_invite_coursemate_is_idempotent(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        course = Course.query.first()

        # We and skippy need to be coursemates.
        test_user.courses.append(course)
        skippy.courses.append(course)

        db.session.commit()

        create_event_url = '/courses/%s/event' % course.id

        new_event_page = client.get(create_event_url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        client.post(create_event_url, data=new_event_request, follow_redirects=True)

        # Event exists now. Let's invite Skippy.

        # Skippy shouldn't have an event yet.
        skippy_id = User.query.filter_by(user_name="skippy").first().id
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id).count()
        self.assertEqual(0, skippy_invite_count)

        self.assertEqual(0, Notification.query.count())

        new_event = Event.query.first()

        event_invite_url = '/courses/%s/events/%s/invitation' % (course.id, new_event.id)

        # Post invitation twice, raising the question, "Does this generate two invites?"

        invitation = {
            'csrf_token': BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value'],
            'everyone': "false",
            'invited': [skippy_id]
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)

        invitation = {
            'csrf_token': BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value'],
            'everyone': "false",
            'invited': [skippy_id]
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)


        test_user_id = User.query.filter_by(user_name="test_user").first().id

        # Skippy should have his invite by now.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count()
        self.assertEqual(1, skippy_invite_count)

        # Skippy should have an invitation.
        self.assertEqual(1, Notification.query.count())


    def test_accepting_invite_event_clears_invitations(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        course = Course.query.first()

        # We and skippy need to be coursemates.
        test_user.courses.append(course)
        skippy.courses.append(course)

        db.session.commit()

        create_event_url = '/courses/%s/event' % course.id

        new_event_page = client.get(create_event_url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        client.post(create_event_url, data=new_event_request, follow_redirects=True)

        # Event exists now. Let's invite Skippy.

        # Skippy shouldn't have an event yet.
        skippy_id = User.query.filter_by(user_name="skippy").first().id
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id).count()
        self.assertEqual(0, skippy_invite_count)

        self.assertEqual(0, Notification.query.count())

        new_event = Event.query.first()

        event_invite_url = '/courses/%s/events/%s/invitation' % (course.id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value']

        invitation = {
            'csrf_token': csrf_token,
            'everyone': "false",
            'invited': [skippy_id]
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        test_user_id = User.query.filter_by(user_name="test_user").first().id

        # Skippy should have his invite by now.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count()
        self.assertEqual(1, skippy_invite_count)

        # Skippy should have an invitation.
        self.assertEqual(1, Notification.query.count())

        invitation = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).first()

        event_invitation_accept_url = '/courses/%s/events/%s/invitations/%s' % (course.id, new_event.id, invitation.id)

        response = self.skippy_client.post(event_invitation_accept_url, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(0, EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count())




    def test_joining_event_clears_invitations(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        course = Course.query.first()

        # We and skippy need to be coursemates.
        test_user.courses.append(course)
        skippy.courses.append(course)

        db.session.commit()

        create_event_url = '/courses/%s/event' % course.id

        new_event_page = client.get(create_event_url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        client.post(create_event_url, data=new_event_request, follow_redirects=True)

        # Event exists now. Let's invite Skippy.

        # Skippy shouldn't have an event yet.
        skippy_id = User.query.filter_by(user_name="skippy").first().id
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id).count()
        self.assertEqual(0, skippy_invite_count)

        self.assertEqual(0, Notification.query.count())

        new_event = Event.query.first()

        event_invite_url = '/courses/%s/events/%s/invitation' % (course.id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value']

        invitation = {
            'csrf_token': csrf_token,
            'everyone': "false",
            'invited': [skippy_id]
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        test_user_id = User.query.filter_by(user_name="test_user").first().id

        # Skippy should have his invite by now.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count()
        self.assertEqual(1, skippy_invite_count)

        # Skippy should have an invitation.
        self.assertEqual(1, Notification.query.count())

        invitation = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).first()

        join_event_url = '/courses/%s/events/%s/attendee' % (course.id, new_event.id)

        skippy_client = self.skippy_client # Grab this and hold on to it so we have continuity.

        csrf_token = skippy_client.get(join_event_url, follow_redirects=True).data

        join = {
            'csrf_token': csrf_token,
            'attending': "true"
        }

        response = skippy_client.post(join_event_url, data=join, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(0, EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count())


    def test_create_event_with_invited_coursemates(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        course = Course.query.first()

        # We and skippy need to be coursemates.
        test_user.courses.append(course)
        skippy.courses.append(course)

        db.session.commit()

        create_event_url = '/courses/%s/event' % course.id

        new_event_page = client.get(create_event_url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "everyone": "false",
            "invited": [skippy.id],
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        client.post(create_event_url, data=new_event_request, follow_redirects=True)

        # Skippy should have an invite.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy.id, sender_id=test_user.id).count()
        self.assertEqual(1, skippy_invite_count)

        # Skippy should have an invitation.
        self.assertEqual(1, Notification.query.count())



    def test_join_event(self):
        client = self.test_client

        # Create the event directly, with Skippy as the owner.
        skippy = User.query.filter(User.user_name=="skippy").first()
        course = Course.query.first()

        event = Event()
        event.course = course
        event.title = "Best Event Ever"
        event.location = "Van Down By The River"
        event.start = datetime.now()+ timedelta(days=1)
        event.end = datetime.now() + timedelta(days=1, hours=2)
        event.owner = skippy

        db.session.add(event)
        db.session.commit()

        test_user = User.query.filter(User.user_name=="test_user").first()

        self.assertEqual(0, test_user.events.count())

        # We have to re-fetch the event because it's not bound to a session. More puzzles from sqlalchemy.
        event = Event.query.first()

        event_attend_url = '/courses/%s/events/%s/attendee' % (event.course.id, event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = client.get(event_attend_url, follow_redirects=True).data

        rsvp = {
            'csrf_token': csrf_token,
            'attending': "true"
        }

        response = client.post(event_attend_url, data=rsvp, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        # Refresh test_user from the DB.
        test_user = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(1, test_user.events.count())



    def test_unjoin_event(self):
        client = self.test_client

        # Create the event directly, with Skippy as the owner.
        skippy = User.query.filter(User.user_name=="skippy").first()
        course = Course.query.first()

        event = Event()
        event.course = course
        event.title = "Best Event Ever"
        event.location = "Van Down By The River"
        event.start = datetime.now()+ timedelta(days=1)
        event.end = datetime.now() + timedelta(days=1, hours=2)
        event.owner = skippy

        db.session.add(event)
        db.session.commit()

        test_user = User.query.filter(User.user_name=="test_user").first()

        # Join the event.
        test_user.events.append(event)
        db.session.commit()

        # Verify that we're attending the event.
        test_user = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(1, test_user.events.count())

        # Let's unjoin
        event_attend_url = '/courses/%s/events/%s/attendee' % (event.course.id, event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = client.get(event_attend_url, follow_redirects=True).data

        rsvp = {
            'csrf_token': csrf_token,
            'attending': "false"
        }

        client.post(event_attend_url, data=rsvp, follow_redirects=True)

        test_user = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(0, test_user.events.count())



    def test_event_comment(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id
        url = '/courses/%s/event' % course_id

        new_event_page = client.get(url, follow_redirects=True)

        new_event_request = {
            "title": "Best Event Ever",
            "location": "Van Down By The River",
            "date": "12/25/14",
            "start": "55800", # 3:30pm
            "end": "61200", # 5:00pm,
            "csrf_token": BeautifulSoup(new_event_page.data).find(id="csrf_token")['value']
        }

        response = client.post(url, data=new_event_request, follow_redirects=True)

        new_event = Event.query.first()

        self.assertEqual(0, EventComment.query.join(Event).filter(Event.id == new_event.id).count())

        url = '/courses/%s/events/%s/comment' % (course_id, new_event.id)

        csrf_token = BeautifulSoup(client.get(url, follow_redirects=True).data).find(id="csrf_token")['value']

        comment_request = {
            "contents": "Best Event Ever",
            "csrf_token": csrf_token
        }

        response = client.post(url, data=comment_request, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(1, EventComment.query.count())

        self.assertEqual("Best Event Ever", EventComment.query.first().contents)

if __name__ == '__main__':
    unittest.main()

