import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
sender = 'saga@f1.hk'
smtp_server = 'seg1.f1.hk'

def send_mail(receiver, subject, body):
    message = MIMEText(body, 'html', 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    smtpObj = smtplib.SMTP(smtp_server, 25)
    smtpObj.sendmail(sender, receiver, message.as_string())
