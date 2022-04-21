from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


# @shared_task()
# def send_email(email_subject,email_content,receivers_email):
#     email = EmailMessage(subject=email_subject, body=email_content, from_email=settings.EMAIL_HOST_USER,
#                          to=receivers_email)
#     email.send()
