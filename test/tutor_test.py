import unittest
import json
from datetime import datetime
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course, TutorApplication
from buddyup.util import time_from_timestamp
from bs4 import BeautifulSoup

class EventTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

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
            TutorApplication.query.delete()


    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
        if login.status == '200 OK': return client



    def test_create_tutor_record(self):
        self.assertEqual(0, TutorApplication.query.count(), "Tutor application shouldn't exist yet.")

        db.session.add(TutorApplication())
        db.session.commit()

        self.assertEqual(1, TutorApplication.query.count())
        
        # User
        # Courses
        # Languages
        # Current Status
        # Location
        # Price



if __name__ == '__main__':
    unittest.main()

