import icalendar
import requests
import datetime
import logging

logger = logging.getLogger(__name__)


def fetch_events(start: datetime, end: datetime, url: str):
    params = dict(
        date_from=start.strftime("%Y-%m-%d"), date_to=end.strftime("%Y-%m-%d")
    )
    logger.info(
        f"Requesting events between {params['date_from']} and {params['date_to']}"
    )
    resp = requests.get(url=url, params=params)
    cal = icalendar.Calendar.from_ical(resp.text)
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
    logger.info(f"Parsed {len(events)} events")
    return sorted(events, key=lambda d: str(d["start"]))
