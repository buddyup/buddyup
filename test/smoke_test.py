import unittest
from datetime import datetime
from buddyup import app
from buddyup.database import User, Visit, db

class SmokeTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

        existing_user = User(user_name="skippy")
        existing_user.initialized = True
        db.session.add(existing_user)
        db.session.commit()

    def tearDown(self):
        if User.query.filter(User.user_name=="skippy").count():
            u = User.query.filter(User.user_name=="skippy")[0]

            Visit.query.filter(Visit.user_id==u.id).delete()
            User.query.filter(User.user_name=="skippy").delete()
        
        db.session.commit()


    def test_homepage(self):
        # This doesn't test a running server, only the local code base in situ.
        tc = app.test_client()
        home = tc.get('/login?username=skippy', follow_redirects=True)

        self.assertTrue("in your class?" in home.data, "That doesn't look like the home page.")


if __name__ == '__main__':
    unittest.main()
