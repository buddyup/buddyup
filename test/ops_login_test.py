import unittest
from datetime import datetime
from buddyup import app

class OpsLoginTests(unittest.TestCase):

    """
    We'd like to be able to login to the ops panel.
    """
    def test_login(self):
        tc = app.test_client()
        home = tc.post('/ops/login', data=dict(username='skippy'), follow_redirects=True)

        self.assertEqual(home.status, '200 OK')
        
if __name__ == '__main__':
    unittest.main()

