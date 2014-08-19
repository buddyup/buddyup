import unittest
from datetime import datetime
from buddyup import app
from buddyup.database import db, Action, User

class TrackActivityTests(unittest.TestCase):

    def setUp(self):
        db.create_all()
        
        # Create a user profile to view.
        skippy = User(user_name="skippy")
        skippy.initialized = True
        db.session.add(skippy)
        db.session.commit()
        
        # Create a user to run our tests as.
        test_user = User(user_name="test_user")
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

    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------
    #-------------------------------------------------------------------------

    def test_track_profile_view(self):
        initial_count = Action.query.count()
        self.test_client.get('/classmates/skippy', follow_redirects=True)
        self.assertEqual(initial_count + 1, Action.query.count(), "A page view wasn't recorded?")

        
if __name__ == '__main__':
    unittest.main()

