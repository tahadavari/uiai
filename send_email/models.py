from django.conf import settings
from django.db import models
from django.core.mail import EmailMessage, EmailMultiAlternatives
# Create your models here.
from core.models import BaseModel


# from send_email.tasks import send_email


class Email(BaseModel):
    TYPE_EMAIL_VERIFY = 1
    TYPE_FORGET_PASSWORD = 2
    TYPE_NEW_USER = 3

    EMAIL_TYPE = [
        (TYPE_EMAIL_VERIFY, 'EMAIL VERIFY'),
        (TYPE_FORGET_PASSWORD, 'FORGET PASSWORD'),
        (TYPE_NEW_USER, 'NEW USER'),
    ]
    receiver_email = models.EmailField()
    email_type = models.IntegerField(choices=EMAIL_TYPE)
    email_content = models.CharField(max_length=50000)
    email_subject = models.CharField(max_length=200)
    email_detail = models.CharField(max_length=500)

    def send_email(self):
        email = EmailMultiAlternatives(subject=self.email_subject, from_email=settings.EMAIL_HOST_USER,
                                       to=[self.receiver_email])
        email.attach_alternative(self.email_content, "text/html")
        email.send()
