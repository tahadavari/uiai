from django.urls import path

from account.api import ProfileGetApi, ProfileUpdateApi,UserInfoApi,WriterRequestApi,AuthorAll,AuthorView,BookmakPostProfile

urlpatterns = [
    path('profile', ProfileGetApi.as_view()),
    path('profile/update', ProfileUpdateApi.as_view()),
    path('profile/info',UserInfoApi.as_view()),
    path('profile/writer-request',WriterRequestApi.as_view()),
    path('profile/bookmark-post',BookmakPostProfile.as_view()),

    path('author/all',AuthorAll.as_view()),
    path('author/view/<str:username>',AuthorView.as_view())
]
