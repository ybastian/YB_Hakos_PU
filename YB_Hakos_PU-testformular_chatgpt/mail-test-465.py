import smtplib, ssl
import webapp.config as config

port = 465  # no starttls
smtp_server = config.Config().EMAIL_HOST
sender_email = config.Config().EMAIL_USERNAME
receiver_email = config.Config().ADMIN_EMAIL
password = config.Config().EMAIL_PASSWORD
message = f"""\
From: {sender_email}
To: {receiver_email}
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port) as server:
    server.set_debuglevel(1)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
