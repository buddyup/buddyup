import unittest
import json
from datetime import datetime
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course, Event, EventInvitation
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
        skippy = User(user_name="skippy")
        skippy.initialized = True
        db.session.add(skippy)
        db.session.commit()

        # Create a user to run our tests as.
        test_user = User(user_name="test_user", full_name="John Smith")
        test_user.initialized = True
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])
        else:
            # Delete users from the memory database, if used.
            User.query.delete()
            Event.query.delete()


    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
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


    def test_invite_event(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id
        create_event_url = '/courses/%s/event' % course_id

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

        new_event = Event.query.first()

        event_invite_url = '/courses/%s/events/%s/invitation' % (course_id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = BeautifulSoup(client.get(event_invite_url, follow_redirects=True).data).find(id="csrf_token")['value']

        invitation = {
            'csrf_token': csrf_token,
            'receiver_id': skippy_id
        }

        response = client.post(event_invite_url, data=invitation, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        test_user_id = User.query.filter_by(user_name="test_user").first().id

        # Skippy should have his invite by now.
        skippy_invite_count = EventInvitation.query.filter_by(receiver_id=skippy_id, sender_id=test_user_id).count()
        self.assertEqual(1, skippy_invite_count, "An event invitation should exist.")



    def test_join_event(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id
        create_event_url = '/courses/%s/event' % course_id

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

        new_event = Event.query.first()

        # Event exists now. Let's join it.

        # First make sure I don't have any events.
        me = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(0, me.events.count())

        event_attend_url = '/courses/%s/events/%s/attendee' % (course_id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = client.get(event_attend_url, follow_redirects=True).data

        rsvp = {
            'csrf_token': csrf_token,
            'attending': "true"
        }

        response = client.post(event_attend_url, data=rsvp, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        me = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(1, me.events.count())



    def test_unjoin_event(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        course_id = Course.query.first().id

        # Create the new event
        new_event = Event()
        new_event.title = "Best Event Ever"
        new_event.location = "Van Down By The River"
        new_event.start = datetime.strptime("12/25/14 3:30pm", '%m/%d/%y %I:%M%p')
        new_event.end = datetime.strptime("12/25/14 5:00pm", '%m/%d/%y %I:%M%p')
        new_event.course_id = course_id

        db.session.add(new_event)
        db.session.commit()

        # Join the event.
        me = User.query.filter_by(user_name="test_user").first()
        me.events.append(new_event)

        # Verify that we're attending the event.
        me = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(1, me.events.count())

        # Let's unjoin
        event_attend_url = '/courses/%s/events/%s/attendee' % (course_id, new_event.id)

        # Grab the csrf token so we can make our request.
        csrf_token = client.get(event_attend_url, follow_redirects=True).data

        rsvp = {
            'csrf_token': csrf_token,
            'attending': "false"
        }

        client.post(event_attend_url, data=rsvp, follow_redirects=True)

        me = User.query.filter_by(user_name="test_user").first()
        self.assertEqual(0, me.events.count())



if __name__ == '__main__':
    unittest.main()

