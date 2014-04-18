import unittest
from datetime import datetime
from buddyup.pages import events

class EventTests(unittest.TestCase):

    def test_parse_time_at_noon(self):

        date = datetime(2014, 1, 15)

        result = events.parse_time("12", "pm", date, "start")
        
        self.assertEqual(result.hour, 12, "Hour should stay at Noon")

        self.assertEqual(result.day, 15, "The day shouldn't change")
        

if __name__ == '__main__':
    unittest.main()

