from mailersend import emails
from app.config import settings

def send_email(to_email: str, subject: str, text_content: str):
    mailer = emails.NewEmail(settings.MAILER_API_KEY)

    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "Ewsd",
        "email": "info@domain.com",
    }

    recipients = [
        {
            "name": "",
            "email": to_email,
        }
    ]
    reply_to = {
        "name": "",
        "email": to_email,
    }


    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(text_content, mail_body)
    mailer.set_reply_to(reply_to, mail_body)
    # mailer.set_plaintext_content("This is the text content", mail_body)

    # using print() will also return status code and data
    mailer.send(mail_body)