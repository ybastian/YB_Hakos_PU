import smtplib, ssl
import webapp.config as config

port = 587  # For starttls
smtp_server = config.Config().EMAIL_HOST
sender_email = config.Config().EMAIL_USERNAME
receiver_email = config.Config().ADMIN_EMAIL
password = config.Config().EMAIL_PASSWORD
message = f"""\
From: {sender_email}
To: {receiver_email}
Subject: Hi there

This message is sent from Python."""

context = ssl._create_unverified_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.set_debuglevel(1)
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
