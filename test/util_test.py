import unittest
from datetime import datetime
from buddyup.util import calendar_event, easy_datetime
from buddyup.database import db, Event

class UtilTests(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def test_export_event_to_calendar_format(self):
        """
        We need a view adapter for Event to support our Calendar widget which 
        eventually takes a JSON list of events.
        """
        start_timestamp = int((easy_datetime("Mar 15 2014 15:00") - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        end_timestamp = int((easy_datetime("Mar 15 2014 17:00") - datetime.utcfromtimestamp(0)).total_seconds() * 1000)

        expected = {
            "id": "1",
            "title": "Tuesday Study Session",
            "start": unicode(start_timestamp),
            "end": unicode(end_timestamp),
            "url": "/courses/42/events/1",
            'class': 'event-warning',            
        }

        event = Event(name="Tuesday Study Session", 
                      start=easy_datetime("Mar 15 2014 15:00"),
                      end=easy_datetime("Mar 15 2014 17:00"),
                      course_id=42
                      )

        # Ensure we have a real ID
        db.session.add(event)
        db.session.commit()

        self.assertEqual(event.id, 1) # Make sure our assumption about ID in the next test is correct.
        
        self.assertDictEqual(expected, calendar_event(event))
        

if __name__ == '__main__':
    unittest.main()

