from exchangelib import DELEGATE, Account, Credentials, Mailbox, Message

credentials = Credentials(
    username='saga.eubts@hotmail.com',  # Or me@example.com for O365
    password='sagaCCXXLL3'
)
account = Account(
    primary_smtp_address='saga.eubts@hotmail.com', 
    credentials=credentials, 
    autodiscover=True, 
    access_type=DELEGATE
)

def send_mail(subject, body):
    email = Message(account=account,
                    folder=account.sent,
                    subject=subject,
                    body=body)
    email.sender = Mailbox(email_address='saga.eubts@hotmail.com')
    email.to_recipients = [Mailbox(email_address='jackal.cho@f1.hk')]
    email.send_and_save()