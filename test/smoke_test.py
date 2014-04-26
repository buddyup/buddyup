import unittest
from datetime import datetime
from buddyup import app

class SmokeTests(unittest.TestCase):

    def test_homepage(self):
        # This doesn't test a running server, only the local code base in situ.
        tc = app.test_client()
        home = tc.get('/login?username=skippy', follow_redirects=True)

        self.assertTrue("Who\'s in Your Class" in home.data, "That doesn't look like the home page.")


if __name__ == '__main__':
    unittest.main()

