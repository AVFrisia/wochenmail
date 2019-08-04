#!/usr/bin/env python3

from email import encoders
from email.utils import localtime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.headerregistry import Address
from icalendar import Calendar, Event
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
            event["end"]["date"], "%Y-%m-%d") - datetime.timedelta(days=1)
        text += event_start.strftime("Vom %d. bis ") + \
            event_end.strftime("%d. %B")

    # choose a way to connect the time to event name
    connections = [" ist ", ": ", " haben wir "]
    text += random.choice(connections)
    text += "<b>" + event["summary"] + "</b>"

    if "description" in event:
        text += "<br><i>" + event["description"] + "</i>"

    return text


def gen_opening():
    openings = ["Liebe Bundesbrüder,",
                "Hochverehrte Bundesbrüder,", "Moin Jungs,", "Werte Bundesbrüder,", "Liebe Aktivitas,"]
    return random.choice(openings)


def gen_closing():
    closings = ["Ich wünsche euch eine schöne Woche!", "Ich freue mich euch da zu sehen!",
                "Allzeit voran!", "Vivat, crescat, floreat AV Frisia!", "Nicht vergessen, immer schön weiter saufen.", "Nicht vergessen: der Östen lebt!"]
    salutes = ["Euer", "Mit besten Frisengrüßen,",
               "Bis zum nächsten Mal,", "Feuchtfröhle Grüße wünscht Euch", "Es grüßt euch aus dem feuchten Keller,", "Ich küsse deine Augen amk"]

    return random.choice(closings) + "<br>" + random.choice(salutes) + "<p>Carl Fs! <i>xx</i><br><small>(Via dem Consenior-Bot)</small></p>"


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
    text = "<html><body><p>" + gen_opening() + "</p>"
    # make list with events
    text += "<p>diese Woche haben wir "

    if len(events) > 1:
        text += str(len(events)) + " Veranstaltungen im Kalender:</p><ul>"
    elif len(events) == 1:
        text += "nur eine Veranstaltung im Kalender:</p><ul>"

    for event in events:
        text += "<li>" + gen_event_text(event) + "</li>"
    text += "</ul>"

    # close it up
    text += "<p>" + gen_closing() + "</p></body></html>"

    return text


def gen_cal_attachment(events):
    cal = Calendar()
    for event in events:
        e = Event()
        e.add("summary", event["summary"])
        if "dateTime" in event["start"]:
            e.add("dtstart", datetime.datetime.strptime(
                event["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S+02:00"))
            e.add("dtend", datetime.datetime.strptime(
                event["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S+02:00"))
        elif "date" in event["start"]:
            e.add("dtstart", datetime.datetime.strptime(
                event["start"]["date"], "%Y-%m-%d"))
            e.add("dtend", datetime.datetime.strptime(
                event["end"]["date"], "%Y-%m-%d"))

        if "description" in event:
            e.add("description", event["description"])

        if "location" in event:
            e.add("location", event["location"])

        cal.add_component(e)

    filename = '/tmp/wochenmail.ics'

    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close()

    return filename


def send_message(bodytext, attachment_path):
    week_number = datetime.datetime.today().strftime("%V")

    # generate a message
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Wochenmail (KW " + week_number + ")"
    msg['From'] = "Johannes Arnold <xx@avfrisia.de>"
    #msg['To'] = "Johannes Arnold <johannes.arnold@stud.uni-hannover.de>"
    msg['To'] = "Aktivitas <ac@avfrisia.de>"
    msg['Date'] = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    msg['X-Mailer'] = "Consenior-Bot v1.1"

    # Generate the MIMEText
    html_text = MIMEText(bodytext, "html")
    plain_text = MIMEText(html2text.html2text(bodytext), "plain")

    # attach the MIMEText
    msg.attach(plain_text)
    msg.attach(html_text)

    # attach the ICS file
    with open(attachment_path, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("text", "calendar")
        part.set_payload(attachment.read())

        attachment.close

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header("Content-Disposition", "attachment",
                        filename="Veranstaltungen.ics")

        # Add attachment to message and convert message to string
        msg.attach(part)

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
        print("Message sent!")

def main():
    event_list = get_events()
    attachment_path = gen_cal_attachment(event_list)
    text = gen_message(event_list)
    send_message(text, attachment_path)
  
if __name__== "__main__":
  main()