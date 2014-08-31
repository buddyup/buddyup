import unittest
import json
from datetime import datetime
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course, Event
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

        self.assertFalse("Missing important information" in response.data, "Error found: %s" % [line for line in response.data.split("\n") if "Missing important information" in line])

        self.assertEqual(1, Event.query.count())

        new_event = Event.query.first()

        self.assertEqual(course_id, new_event.course_id)

        self.assertEqual(user_id, new_event.owner_id)

        self.assertEqual("03:30PM", new_event.start.strftime("%I:%M%p"))

        self.assertEqual("05:00PM", new_event.end.strftime("%I:%M%p"))


if __name__ == '__main__':
    unittest.main()

