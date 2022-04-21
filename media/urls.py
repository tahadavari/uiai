from django.urls import path

from media.api import UploadPostImageApi

urlpatterns = [
    path('upload-post-image', UploadPostImageApi.as_view()),
]
