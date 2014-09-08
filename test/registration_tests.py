import unittest
import os
from buddyup import app
from buddyup.database import db, User
from bs4 import BeautifulSoup

class InvitationTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])
        else:
            db.drop_all()

    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    def test_access_registration_screen(self):
        """
        Starting from the Start page, can we get to the Registration screen after authenticating?
        """
        client = app.test_client()

        # Verify we can get to the Start page to begin.
        result = client.get('/start', follow_redirects=True)

        self.assertEqual('200 OK', result.status)
        self.assertIn('Welcome!', result.data)

        # In Development Mode, AUTHENTICATION_SCHEME = 'google'. See config.py.

        # Pretend we've been authenticated.
        # This is tricky, because you set the session inside the 'with' block,
        # but you have to pull back out of the block to make your requests.
        # So watch your formatting.
        with client.session_transaction() as session:
            session["gplus_id"] = '123123123123123123123'

        # We should now get taken along to the Register page when we 'return' to the site.
        result = client.get('/login', follow_redirects=True)

        self.assertEqual('200 OK', result.status)
        self.assertIn('Register', result.data)


    def test_register_new_user(self):
        client = app.test_client()
        # Simulate Google authentication. See notes elsewhere in this suite.
        with client.session_transaction() as session:
            session["gplus_id"] = '123123123123123123123'

        self.assertEqual(0, User.query.count())

        registration_page = client.get('/login', follow_redirects=True)

        # Submit the minimum required fields.
        # BUDDYUP_REQUIRE_PHOTO is False in Dev Mode. See config.py
        registration_request = {
            "full_name": "Benjamin Franklin",
            'term_condition': 'checked',
            "csrf_token": BeautifulSoup(registration_page.data).find(id="csrf_token")['value']
        }

        result = client.post('/register', data=registration_request, follow_redirects=True)

        # Make sure we've gone on to the final page.
        self.assertIn("You're In!", result.data)

        self.assertEqual(1, User.query.count())

        self.assertTrue(User.query.first().initialized, "User hasn't actually be created, only the record.")

        self.assertEqual("Benjamin Franklin", User.query.first().full_name)



if __name__ == '__main__':
    unittest.main()

