from django.urls import path

from media.api import UploadPostImageApi

urlpatterns = [
    path('upload-file', UploadPostImageApi.as_view()),
]
