from django.urls import path

from general.api import *

urlpatterns = [
    path('about-us', AboutUsApi.as_view()),
    path('contact-us', ContactUsApi.as_view()),
    path('contact-us/form', ContactFormApi.as_view()),
    path('newsletter', NewsletterApi.as_view()),

    path('home', LandingApi.as_view()),
]
