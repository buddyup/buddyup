import unittest
from datetime import datetime
from buddyup import app
from buddyup.database import (Operator, db)
import hashlib

class OpsLoginTests(unittest.TestCase):

    def setUp(self):
        db.create_all()
        
        op = Operator(login='skippy', password=hashlib.sha256('peterpan').hexdigest())
        db.session.add(op)
        db.session.commit()

    def tearDown(self):
        import os
        if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'] != 'sqlite:///:memory:':
            os.remove(os.environ['DATABASE_URL'])

    """
    We'd like to be able to login to the ops panel.
    """
    def test_login(self):
        tc = app.test_client()
        home = tc.post('/ops/login', data=dict(login='skippy', password='peterpan'), follow_redirects=True)
        
        self.assertEqual(home.status, '200 OK')
        
if __name__ == '__main__':
    unittest.main()

