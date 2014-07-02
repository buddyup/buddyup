import unittest
import os
from datetime import datetime
from buddyup import app
from buddyup.database import db, Action, User, BuddyInvitation
from buddyup.pages.buddyinvitations import compose_invitation_message

class InvitationTests(unittest.TestCase):

    def setUp(self):
        db.create_all()
        
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
            # Delete objects from the memory database, if used.
            User.query.delete()
            BuddyInvitation.query.delete()
    
    @classmethod
    def tearDownClass(self):
        if os.path.isfile("last_sent.msg"):
            os.remove("last_sent.msg")

    @property
    def test_client(self):
        """
        Return a logged-in test client.
        """
        client = app.test_client()
        login = client.get('/login?username=test_user', follow_redirects=True)
        if login.status == '200 OK': return client

    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------

    def test_buddy_invite(self):
        self.assertEqual(0, BuddyInvitation.query.count(), "No invites should exist yet.")
        
        self.test_client.get('/invite/send/skippy', follow_redirects=True)
        
        self.assertEqual(1, BuddyInvitation.query.count(), "An invite wasn't created?")

        email_sent = open("last_sent.msg").read()
        
        self.assertIsNotNone(email_sent)
        self.assertIn("You have received a buddy request from John Smith on BuddyUp.", email_sent, "Sender's name isn't showing up in the email.")
        
        
if __name__ == '__main__':
    unittest.main()

