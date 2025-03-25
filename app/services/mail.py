from app.config import settings
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



def send_email(to_email: str, subject: str, text_content: str):
    message = Mail(
        from_email='ta.thihaaungg@gmail.com',
        to_emails=to_email,
        subject=subject,
        html_content=text_content
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
