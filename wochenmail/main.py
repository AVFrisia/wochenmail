#!/usr/bin/env python3
import locale
import datetime
import random
from calendarhandler import get_events, parse_events

from mailhandler import send_mail

from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger

locale.setlocale(locale.LC_ALL, str("de_DE.UTF-8"))

from jinja2 import Environment, FileSystemLoader, select_autoescape

environment = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape(default=True),
)

template = environment.get_template("plain.html")


def wochenmail(to):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(weeks=1)
    url = "https://intern.avfrisia.de/adm_program/modules/events/events_ical.php"
    cal = get_events(start, end, url)
    events = parse_events(cal)

    subj = start.strftime("Wochenmail KW %V")

    opening = random.choice(
        ["Liebe Bundesbrüder,", "Hochverehrte Bundesbrüder,", "Werte Bundesbrüder,"]
    )

    message = (
        f"diese Woche haben wir {len(events)} Veranstaltungen:"
        if len(events) > 1
        else "diese Woche haben wir nur eine Versanstaltung:"
    )

    closure = random.choice(
        [
            "Einen guten Start in die Woche wünscht euch",
            "Viel Spaß dabei!",
            "Viele Grüße",
        ]
    )

    msg = template.render(
        title=subj,
        opening=opening,
        message=message,
        events=events,
        closure=closure,
        signature="Euer Vorstand",
    )

    send_mail(to, subj, msg)


def main():
    with Scheduler() as scheduler:
        trigger = CronTrigger(day_of_week="mon", hour=0)

        scheduler.add_schedule(
            wochenmail,
            trigger=trigger,
            kwargs={"to": "ac@avfrisia.de"},
        )

        scheduler.run_until_stopped()


if __name__ == "__main__":
    main()
