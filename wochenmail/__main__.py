#!/usr/bin/env python3
import locale
from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger
from email.headerregistry import Address
import logging
import datetime
from email.headerregistry import Address
import random
from jinja2 import Environment, FileSystemLoader, select_autoescape
from wochenmail.calendarhandler import fetch_events
from wochenmail.mailhandler import send_mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, str("de_DE.UTF-8"))

environment = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape(default=True),
)

template = environment.get_template("plain.html")


def send_wochenmail(to):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(weeks=1)
    url = "https://intern.avfrisia.de/adm_program/modules/events/events_ical.php"
    events = fetch_events(start, end, url)

    subj = start.strftime("Wochenmail KW %V")

    opening = random.choice(
        ["Liebe Bundesbrüder,", "Hochverehrte Bundesbrüder,", "Werte Bundesbrüder,"]
    )

    if len(events) == 1:
        message = "diese Woche steht nur eine Veranstaltung an:"
    elif len(events) == 0:
        message = "diese Woche stehen keine Veranstaltungen an."
    else:
        message = f"diese Woche stehen {len(events)} Veranstaltungen an:"

    closure = random.choice(
        [
            "Einen guten Start in die Woche wünscht euch",
            "Viel Spaß dabei!",
            "Viele Grüße",
            "Mit freundlichen Grüßen",
            "Freundliche Grüße",
            "Mit besten Grüßen",
            "Hochachtungsvoll",
            "Mit vorzüglicher Hochachtung",
            "Mit bester Empfehlung",
            "Mit Brudergruß und Handschlag",
            "Mit bundesbrüderlichen Grüßen",
            "GaLiGrü",
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

    from_addr = Address("Consenior der AV Frisia", "xx", "avfrisia.de")

    send_mail(from_addr, to, subj, msg)


def main():
    test = Address("Johannes", "johannes", "rnold.online")
    send_wochenmail(test)

    ac = Address("Aktivitas", "ac", "avfrisia.de")
    with Scheduler() as scheduler:
        trigger = CronTrigger(day_of_week="mon", hour=0)

        scheduler.add_schedule(
            send_wochenmail,
            trigger=trigger,
            kwargs={"to": ac},
        )

        scheduler.run_until_stopped()


if __name__ == "__main__":
    main()
