#!/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage

toaddrs  = 'sudo@esss.se'
fromaddr = 'noreply@esss.se'
fileToSend = '/tmp/sample.pdf'

def send_message():
    msg = MIMEMultipart('alternative')
    s = smtplib.SMTP('mail.esss.lu.se', 25)
    s.ehlo()
    s.starttls()
    s.login('kalle', 'kalle')

    toEmail, fromEmail = toaddrs, fromaddr
    msg['Subject'] = 'Your sebcard file'
    msg['From'] = fromEmail
    body = 'Have Fun'

    content = MIMEText(body, 'plain')
    msg.attach(content)
    filename = fileToSend
    f = file(filename)
    attachment = MIMEText(f.read())
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
    msg.attach(attachment)
    s.sendmail(fromEmail, toEmail, msg.as_string())

send_message()

