from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView, TokenObtainPairView

from authenticate.api import RegisterApi, MyTokenObtainPairView, MyTokenRefreshView, VerifyEmailApi, LogoutApi, \
    ForgetPassword, ResetPassword, VerifyPhoneNumberApi, VerifyOTPApi

urlpatterns = [
    path('register', RegisterApi.as_view()),
    path('login', MyTokenObtainPairView.as_view()),
    path('logout', LogoutApi.as_view()),
    path('refresh-token', MyTokenRefreshView.as_view()),
    path('verify-token', TokenVerifyView.as_view()),
    path('verify-email/<str:token>', VerifyEmailApi.as_view()),
    path('forget-password', ForgetPassword.as_view()),
    path('reset-password', ResetPassword.as_view()),
    path('verify-phone-number',VerifyPhoneNumberApi.as_view()),
    path('verify-otp',VerifyOTPApi.as_view())
]
