import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv
from html2text import html2text
from css_inline import inline
from minify_html import minify

context = ssl.create_default_context()


def send_mail(to, subject, htmlmessage):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = getenv("SMTP_USER")
    message["To"] = to

    htmlmessage = inline(minify(htmlmessage))

    plaintext = MIMEText(html2text(htmlmessage), "plain")
    text = MIMEText(htmlmessage, "html")

    message.attach(plaintext)
    message.attach(text)

    host = getenv("SMTP_HOST")
    port = int(getenv("SMTP_PORT", 587))
    user = getenv("SMTP_USER")
    passwd = getenv("SMTP_PASSWORD")

    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(user, passwd)
        server.sendmail(user, to, message.as_string())

    print(f"Sent mail to {to}")
