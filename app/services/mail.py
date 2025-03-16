# import mailersend
# from app.config import settings

# def send_email(to_email: str, subject: str, text_content: str):
#     mailer = mailersend.NewApiClient(api_key=settings.MAILER_API_KEY)

#     subject = "OTP Code"
#     text = text_content
#     html = text_content

#     my_mail = "info@domain.com"
#     subscriber_list = [to_email]

#     mailer.send(my_mail, subscriber_list, subject, html, text_content)