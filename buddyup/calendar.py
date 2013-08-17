from buddyup.database import Event

def calendar(start, end):
    query = Event.query
    query = query.filter(Event.time >= start)
    query = query.filter(Event.time <= end)
    return events_to_json(query.all())


def events_to_json(events):
    json = []
    for event in events:
        date = event.date.strftime("%Y-%m-%d %H:%M")
        json.append({
            'id': event.id,
            'title': event.name,
            'start': date,
            'end': date,
            'url': url_for('event_view', event_id=event.id),
        })
    return json
