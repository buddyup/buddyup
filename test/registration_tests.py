import unittest
import os
from datetime import datetime
from buddyup import app
from buddyup.database import db, Action, User, BuddyInvitation, Notification, Buddy
from buddyup.pages.buddyinvitations import buddy_up
import flask

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
    def test_registration(self):

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



if __name__ == '__main__':
    unittest.main()

