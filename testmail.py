#!/bin/env python

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage

daUsername = 'kalle'
daUserpasswd = 'kalle'

message = MIMEMultipart()
message['Subject'] = "Attachment Test"
message['From'] = 'noreply@esss.se'
message['Reply-to'] = 'noreply@esss.se'
message['To'] = 'sudo@esss.se'

text = MIMEText("Message Body")
message.attach(text)

directory = '/tmp/sample.pdf'
with open(directory, encoding = 'utf-8', errors = 'replace') as opened:
    openedfile = opened.read()
attachedfile = MIMEApplication(openedfile, _subtype = "pdf", _encoder = encode_base64)
attachedfile.add_header('content-disposition', 'attachment', filename = "sample.pdf")
message.attach(attachedfile)

s = smtplib.SMTP('mail.esss.lu.se', 25)
s.ehlo()
s.starttls()
s.login(daUsername, daUserpasswd)
s.sendmail(message['From'], message['To'], message.as_string())
s.quit()
