from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect
from hashids import Hashids
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from django.template.loader import render_to_string

from account.models import User
from account.serializers import UserSerializer
from authenticate.models import EmailVerifyToken, ForgetPasswordEmailToken
from authenticate.serializers import RegisterSerializer, MyTokenObtainPairSerializer, LogoutSerializer, \
    ResetPasswordSerializer
from send_email.models import Email
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from core.permissions import IsAuthenticated

hashids_verify_email = Hashids(salt=settings.EMAIL_VERIFY_SALT, min_length=10)
hashids_reset_password = Hashids(salt=settings.RESET_PASSWORD_SALT, min_length=10)


class RegisterApi(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_serializer = UserSerializer(data=serializer.data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        data = {
            'message': 'Registration completed successfully',
            'success': True
        }
        self.send_verify_email(user)
        return Response(data, status=status.HTTP_200_OK)

    def send_verify_email(self, user):
        if EmailVerifyToken.objects.filter(user=user).first():
            email_verify_token = EmailVerifyToken.objects.filter(user=user).first()
            token = email_verify_token.token
        else:
            token = hashids_verify_email.encode(int(user.id), datetime.now().microsecond)
            email_verify_token = EmailVerifyToken(user=user, token=token)
            email_verify_token.save()

        email_subject = "Activate your account"
        email_detail = {
            'first_name': user.first_name,
            'url': settings.EMAIL_VERIFY_URL + token
        }
        email_content = render_to_string("email/email_verify.html", context=email_detail)
        email = Email(email_content=email_content, email_subject=email_subject, email_type=Email.TYPE_EMAIL_VERIFY,
                      receiver_email=user.email, email_detail=email_detail)
        email.save()
        email.send_email()


class MyTokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        request.session['refresh-token'] = data["refresh"]
        response = Response(
            {'access': data["access"]}, status=status.HTTP_200_OK)
        return response


class MyTokenRefreshView(generics.GenericAPIView):
    serializer_class = TokenRefreshSerializer

    def get(self, request, *args, **kwargs):
        refresh_token = request.session.get(
            'refresh-token') if request.session.get('refresh-token') else ''

        data = {'refresh': refresh_token}

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        serializer_data = serializer.validated_data
        response = Response(serializer_data, status=status.HTTP_200_OK)
        return response


class LogoutApi(generics.GenericAPIView):
    def post(self, request):
        if request.session.get('refresh-token'):
            del request.session['refresh-token']
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'session not found'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailApi(APIView):

    def get(self, request, token):
        email_verify = EmailVerifyToken.objects.filter(token=token).first()
        if email_verify:
            user = email_verify.user
            user.verify_email = True
            user.save()
            email_verify.delete()
        return redirect(settings.LOGIN_URL)


class ForgetPassword(generics.GenericAPIView):

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            self.send_reset_password_email(user)
        else:
            self.send_not_found_user_email(email)
        return Response(data={'message': 'ایمیل با موفقیت ارسال شد', 'success': True}, status=status.HTTP_200_OK)

    def send_reset_password_email(self, user):
        forget_password = ForgetPasswordEmailToken.objects.filter(user=user).first()
        if forget_password and forget_password.is_valid():
            token = forget_password.token
        else:
            token = hashids_reset_password.encode(int(user.id), datetime.now().microsecond)
            forget_password = ForgetPasswordEmailToken(user=user, token=token)
            forget_password.delete_user_tokens()
            forget_password.save()

        email_subject = "Reset your password"
        email_detail = {
            'first_name': user.first_name,
            'url': settings.RESET_PASSWORD_URL + token
        }
        email_content = render_to_string("email/reset_password.html", context=email_detail)
        email = Email(email_content=email_content, email_subject=email_subject, email_type=Email.TYPE_FORGET_PASSWORD,
                      receiver_email=user.email, email_detail=email_detail)
        email.save()
        email.send_email()

    def send_not_found_user_email(self, email):
        email_subject = "Reset your password"
        email_detail = {
            'url': settings.REGISTER_URL
        }
        email_content = render_to_string("email/new_user.html", context=email_detail)
        email = Email(email_content=email_content, email_subject=email_subject, email_type=Email.TYPE_EMAIL_VERIFY,
                      receiver_email=email, email_detail=email_detail)
        email.save()
        email.send_email()


class ResetPassword(generics.GenericAPIView):
    def post(self, request):
        reset_password_serializer = ResetPasswordSerializer(data=request.data)
        reset_password_serializer.is_valid(raise_exception=True)
        reset_password_serializer.save()
        return Response(data={'message': 'رمز عبور با موفقیت تغییر کرد', 'success': True}, status=status.HTTP_200_OK)


class VerifyPhoneNumberApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        phone_number = request.data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'error': 'این شماره تلفن قبلا به ثبت رسده است'}, status=status.HTTP_400_BAD_REQUEST)
        user.send_otp_verify_phone_number(phone_number)
        return Response({'success': True}, status=status.HTTP_200_OK)


class VerifyOTPApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data.get('token')
        if token == '123456':
            user.level = User.LEVEL_WRITER
            user.save()
            refresh = MyTokenObtainPairSerializer.get_token(user)
            request.session['refresh-token'] = str(refresh)
            return Response({'message': 'شماره تلفن با موفقیت ثبت شد', 'success': True}, status=status.HTTP_200_OK)
        return Response({'error': 'کد اعتبار سنجی فاقد اعتبار است'}, status=status.HTTP_400_BAD_REQUEST)
