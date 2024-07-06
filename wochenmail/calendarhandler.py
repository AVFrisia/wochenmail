import icalendar
import requests
import datetime
from operator import itemgetter


def get_events(start: datetime, end: datetime, url: str) -> icalendar.Calendar:
    params = dict(
        date_from=start.strftime("%Y-%m-%d"), date_to=end.strftime("%Y-%m-%d")
    )
    resp = requests.get(url=url, params=params)
    return icalendar.Calendar.from_ical(resp.text)


def parse_events(cal: icalendar.Calendar):
    events = list()
    for event in cal.walk("VEVENT"):
        events.append(
            {
                "name": event.get("SUMMARY"),
                "description": event.get("DESCRIPTION"),
                "location": event.get("location"),
                "start": event.decoded("DTSTART"),
                "end": event.decoded("DTEND"),
            }
        )
    return sorted(events, key=itemgetter("start"))
