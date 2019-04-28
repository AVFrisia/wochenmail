#!/usr/bin/env python3

from email.utils import localtime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.headerregistry import Address
import configparser
import ssl
import smtplib
from smtplib import SMTP
import json
import requests
import datetime
import locale
import html2text
import random

locale.setlocale(locale.LC_ALL, str('de_DE.UTF-8'))

# load the settings
config = configparser.ConfigParser()
config.read("settings.ini")


def get_events():
    current_time = datetime.datetime.today()
    now_string = current_time.isoformat("T") + "Z"
    then_time = current_time + datetime.timedelta(weeks=1)
    then_string = then_time.isoformat("T") + "Z"
    config = configparser.ConfigParser()
    config.read("settings.ini")
    url = "https://www.googleapis.com/calendar/v3/calendars/2oj4t3ocqj3u3uas7o6gflro68@group.calendar.google.com/events"
    params = dict(
        key=config["calendar"]["key"],
        orderBy="starttime",
        singleEvents="true",
        timeMin=now_string,
        timeMax=then_string
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()  # Check the JSON Response Content documentation below

    return data["items"]


def gen_event_text(event):
    text = ""

    # Text to describe time
    if "dateTime" in event["start"]:
        event_date = datetime.datetime.strptime(
            event["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S+02:00")
        text += event_date.strftime("Am %A, der %d.%m um %H:%M")
    elif "date" in event["start"]:
        event_start = datetime.datetime.strptime(
            event["start"]["date"], "%Y-%m-%d")
        event_end = datetime.datetime.strptime(
            event["end"]["date"], "%Y-%m-%d")
        text += event_start.strftime("Vom %d. bis ") + \
            event_end.strftime("%d. %B")

    # choose a way to connect the time to event name
    connections = [" ist ", ": ", " haben wir "]
    text += random.choice(connections)
    text += "<b>" + event["summary"] + "</b>"

    if "description" in event:
        text += "<br><i>" + event["description"] + "</i>"

    return text


def gen_closing():
    closings = ["Ich wünsche euch eine schöne Woche!", "Ich freue mich euch da zu sehen!",
                "Allzeit voran!", "Vivat, crescat, floreat AV Frisia!", "Nicht vergessen, immer schön weiter saufen."]
    salutes = ["Euer", "Mit besten Frisengrüßen,",
               "Bis zum nächsten Mal,", "Feuchtfröhle Grüße wünscht Euch", "Es grüßt euch aus dem feuchten Keller,", "Ich küsse deine Augen amk"]

    return random.choice(closings) + "<br>" + random.choice(salutes) + "<br>Der Consenior-Bot Fs! <i>xx</i>"


def gen_message(events):
    if not events:
        return """
            <html>
                <body>
                    <p>Liebe Bundesbrüder,</p>
                    <p>diese Woche gibt es keine Veranstaltungen.</p>
                    <p>Euer<br>Consenior-Bot Fs! <i>xx</i></p>
                </body>
            </html>
        """
    # prepare standard text
    text = """<html>
            <body>
                <p>Liebe Bundesbrüder,</p>
    """
    # make list with events
    text += "<p>diese Woche haben wir " + \
        str(len(events)) + " Veranstaltungen im Kalender:</p>"
    text += "<ul>"
    for event in events:
        text += "<li>" + gen_event_text(event) + "</li>"
    text += "</ul>"

    # close it up
    text += "<p>" + gen_closing() + "</p></body></html>"

    return text


def send_message(bodytext):
    week_number = datetime.datetime.today().strftime("%V")

    # generate a message
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Wochenmail (KW " + week_number + ")"
    msg['From'] = "Consenior-Bot <xx@avfrisia.de>"
    msg['To'] = "Johannes Arnold <johannes.arnold@stud.uni-hannover.de>"
    msg['Date'] = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    msg['X-Mailer'] = "Consenior-Bot v1.0"

    # Generate the MIMEText
    html_text = MIMEText(bodytext, "html")
    plain_text = MIMEText(html2text.html2text(bodytext), "plain")

    # attach the MIMEText
    msg.attach(plain_text)
    msg.attach(html_text)

    # load the settings
    config = configparser.ConfigParser()
    config.read("settings.ini")
    hostname = config["smtp"]["server"]
    port = config["smtp"]["port"]
    username = config["smtp"]["username"]
    password = config["smtp"]["password"]

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(hostname, port, context=context) as server:
        # server.set_debuglevel(3)
        server.login(username, password)
        # after login, send the mail
        server.send_message(msg)


event_list = get_events()
print(gen_message(event_list))
text = gen_message(event_list)
send_message(text)
