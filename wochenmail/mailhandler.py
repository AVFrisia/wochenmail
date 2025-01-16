import smtplib, ssl
from email.message import EmailMessage
from email.utils import localtime
from os import getenv
from html2text import html2text
from css_inline import inline
import logging

logger = logging.getLogger(__name__)
context = ssl.create_default_context()


def send_mail(from_addr, to_addr, subject, htmlmessage):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_addr
    message["To"] = to_addr
    message["Date"] = localtime()

    htmlmessage = inline(message)
    plaintext = html2text(htmlmessage)

    message.set_content(plaintext)
    message.add_alternative(htmlmessage, subtype="html")

    host = getenv("SMTP_HOST")
    port = int(getenv("SMTP_PORT", 587))
    user = getenv("SMTP_USER")
    passwd = getenv("SMTP_PASSWORD")

    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(user, passwd)
        server.send_message(message)
        logger.info(f"Sent mail to {to_addr}")
