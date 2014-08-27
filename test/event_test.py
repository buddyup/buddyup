import unittest
from datetime import datetime
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course

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

    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
        if login.status == '200 OK': return client


    def test_parse_time_at_noon(self):

        date = datetime(2014, 1, 15)

        result = events.parse_time("12", "pm", date, "start")
        
        self.assertEqual(result.hour, 12, "Hour should stay at Noon")

        self.assertEqual(result.day, 15, "The day shouldn't change")


    def test_json_for_events(self):

        result = self.test_client.get('/courses/1/events.json', follow_redirects=True)

        self.assertEqual(result.status_code, 200)

        # JSON should be empty before there are events.
        self.assertEqual(result.data, "{}")

        result = self.test_client.get('/courses/1/events.json', follow_redirects=True)
        
        self.assertNotEqual(result.data, "{}")

        # JSON should have a single Event afterwards.

        

if __name__ == '__main__':
    unittest.main()

