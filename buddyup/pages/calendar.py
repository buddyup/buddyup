from buddyup.database import Event

def calendar(start, end):
    query = Event.query
    query = query.filter(Event.time >= start)
    query = query.filter(Event.time <= end)
    return events_to_json(query.all())


def events_to_json(events):
    json = []
    for event in events:
        date = event.date.strftime("%Y-%m-%d")
        json.append({
            'id': event.id,
            'title': event.name,
            'start': date,
            'end': date,
        })
    return json