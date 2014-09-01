import unittest
import os
from datetime import datetime
from buddyup import app
from buddyup.database import db, Action, User, BuddyInvitation, Notification, Buddy
from buddyup.pages.buddyinvitations import buddy_up

class InvitationTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

        # Create a user profile to invite.
        skippy = User(user_name="skippy", full_name="Skippy Johnson")
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
            db.drop_all()

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


    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------

    def test_buddy_invite_basic_workflow(self):
        self.assertEqual(0, BuddyInvitation.query.count(), "No invites should exist yet.")
        self.assertEqual(0, Notification.query.count(), "No notifications should exist yet.")

        self.test_client.post('/classmates/skippy/invitation', data={}, follow_redirects=True)

        self.assertEqual(1, BuddyInvitation.query.count(), "An invite wasn't created?")
        self.assertEqual(1, Notification.query.count(), "Where is the Notification about the invite?")

        # Now we need to make sure that the link we got in the Notification is right.
        notification = Notification.query.first()

        self.assertEqual("/classmates/skippy/invitations/test_user", notification.action_link)

        # TODO: Figure out why SQLalchemy errors if I use the action_link directly in the post() call,
        # but works just fine if I put that value into another variable here:
        url = notification.action_link

        # Now switch over to Skippy's point of view. (He is receiving the invite.)
        result = self.skippy_client.post(url, data={}, follow_redirects=True)

        self.assertEqual('200 OK', result.status)

        skippy = db.session.query(User).filter(User.user_name=="skippy").first()
        buddies = db.session.query(User).filter(User.user_name=="test_user").first().buddies.all()

        self.assertIn(skippy.id, [b.id for b in buddies], "No buddy relationship was created.")


    def test_buddy_up(self):
        """
        Test the underlying 'buddy_up' utility function directly.
        """
        test_user = User.query.filter(User.user_name=="test_user").first()
        skippy = User.query.filter(User.user_name=="skippy").first()

        buddy_up(test_user, skippy)

        self.assertIn(test_user, skippy.buddies)
        self.assertIn(skippy, test_user.buddies)



if __name__ == '__main__':
    unittest.main()

