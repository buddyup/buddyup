import unittest
import json
from datetime import datetime
from buddyup.pages import events
from buddyup.app import app
from buddyup.database import db, User, Course, Tutor, Language, Location
from buddyup.util import time_from_timestamp
from bs4 import BeautifulSoup

def ids(entities):
    return [e.id for e in entities];

class TutorTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

        # Create a user to run our tests as.
        test_user = User(user_name="test_user", full_name="John Smith")
        test_user.initialized = True
        db.session.add(test_user)

        db.session.add(Course(name="Course 1"))
        db.session.add(Course(name="Course 2"))
        db.session.add(Course(name="Course 3"))

        db.session.add(Language(name="Esperanto"))
        db.session.add(Language(name="Klingonese"))

        db.session.add(Location(name="Los Angeles"))
        db.session.add(Location(name="Vancouver"))


        db.session.commit()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])
        else:
            # Delete users from the memory database, if used.
            User.query.delete()
            Tutor.query.delete()


    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
        if login.status == '200 OK': return client


    def test_tutor_application(self):
        client = self.test_client # Only initiate the client once during this test since we maintain state.
        user_id = User.query.filter(User.user_name=="test_user").first().id
        url = '/tutors/'

        self.assertEqual(0, Tutor.query.count(), "No applications should exist yet.")

        tutor_application_page = client.get(url, follow_redirects=True)

        self.assertEqual('200 OK', tutor_application_page.status)

        tutor_application_request = {
            "courses": ids(Course.query.limit(3)),
            "languages": ids([Language.query.first()]),
            "status": "looking",
            "location": ids([Location.query.first()]),
            "price": "13.00",
            "per": "hour",
            "csrf_token": BeautifulSoup(tutor_application_page.data).find(id="csrf_token")['value']
        }

        response = client.post(url, data=tutor_application_request, follow_redirects=True)

        self.assertEqual('200 OK', response.status)

        self.assertEqual(1, Tutor.query.count())

        new_tutor = Tutor.query.first()

        self.assertEqual(user_id, new_tutor.user_id)

        self.assertEqual(1, new_tutor.languages.count())

        self.assertEqual(Language.query.first(), new_tutor.languages.first())




if __name__ == '__main__':
    unittest.main()

