import unittest
from datetime import datetime
from buddyup import app
from buddyup.database import User, Visit, db
import hashlib

def is_home_screen(page):
    return "Who's in Your Class" in page.data

def is_profile_setup_screen(page):
    return "This information will appear in your public profile." in page.data


class GeneralLoginTests(unittest.TestCase):

    # IMPORTANT NOTE: The CAS-based tests require MockCAS to be running.
    # TODO: Incorporate MockCAS into this test suite instead of running it separately.

    def setUp(self):
        db.create_all()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])
        else:
            # Delete users from the memory database, if used.
            User.query.delete()

    def test_new_login_with_CAS(self):
        # Indicate we're using CAS
        app.config['BUDDYUP_ENABLE_AUTHENTICATION'] = True
        
        tc = app.test_client()
        
        home = tc.get('/login?ticket=faketicket', follow_redirects=True)
        
        self.assertEqual(home.status, '200 OK')
        
        self.assertTrue("This information will appear in your public profile." in home.data)


    def test_existing_login_with_CAS(self):

        app.config['BUDDYUP_ENABLE_AUTHENTICATION'] = True
    
        initial_visits = Visit.query.count()
    
        existing_user = User(user_name="mockuser")
        existing_user.initialized = True
        db.session.add(existing_user)
        db.session.commit()
    
        tc = app.test_client()
        home = tc.get('/login?ticket=faketicket&username=mockuser', follow_redirects=True)
        
        self.assertEqual(home.status, '200 OK')
    
        self.assertTrue(is_home_screen(home))
    
        self.assertEqual(initial_visits + 1, Visit.query.count())
    
    
    def test_login_without_CAS(self):
    
        # Indicate we're NOT using CAS
        app.config['BUDDYUP_ENABLE_AUTHENTICATION'] = False
        
        tc = app.test_client()
        home = tc.get('/login?username=testuser', follow_redirects=True)
        
        self.assertEqual(home.status, '200 OK')
    
        # Expect to be on the Profile Setup screen since we've just been added to the system.
        profile_setup_text = "This information will appear in your public profile."
        self.assertTrue(is_profile_setup_screen(home))

        
if __name__ == '__main__':
    unittest.main()

