from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.template.loader import render_to_string
from hashids import Hashids
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _

# Register serializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User

from authenticate.models import EmailVerifyToken, ForgetPasswordEmailToken
from send_email.models import Email

hashids_verify_email = Hashids(salt=settings.EMAIL_VERIFY_SALT, min_length=10)


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email', 'password', 'confirm_password']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False},
            'confirm_password': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
        }

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise PermissionDenied(
                {'confirm_password': ["Those passwords don't match."]})
        return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': {'error': _('کاربری با این مشخصات یافت نشد')}
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['level'] = user.level
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if not self.user.verify_email:
            if EmailVerifyToken.objects.filter(user=self.user).first():
                email_verify_token = EmailVerifyToken.objects.filter(user=self.user).first()
                token = email_verify_token.token
            else:
                token = hashids_verify_email.encode(int(self.user.id), datetime.now().microsecond)
                email_verify_token = EmailVerifyToken(user=self.user, token=token)
                email_verify_token.save()

            email_subject = "Activate your account"
            email_detail = {
                'first_name': self.user.first_name,
                'url': settings.EMAIL_VERIFY_URL + token
            }
            email_content = render_to_string("email/email_verify.html", context=email_detail)
            email = Email(email_content=email_content, email_subject=email_subject, email_type=Email.TYPE_EMAIL_VERIFY,
                          receiver_email=self.user.email, email_detail=email_detail)
            email.save()
            email.send_email()
            raise PermissionDenied(detail={'error': "لطفا ایمیل خود را تایید کنید"})

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'error': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        fields = ['token', 'password', 'confirm_password']
        extra_kwargs = {
            'token': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False},
            'confirm_password': {'required': True, 'allow_blank': False},
        }

    def validate(self, data):
        self.password = data.get('password')
        self.forget_password = ForgetPasswordEmailToken.objects.filter(token=data.get('token')).first()
        if not self.forget_password or not self.forget_password.is_valid():
            raise PermissionDenied(
                {'error': "token is expire or invalid"})
        elif data.get('password') != data.get('confirm_password'):
            raise PermissionDenied(
                {'error': "Those passwords don't match."})
        return data

    def save(self, **kwargs):
        user = self.forget_password.user
        user.set_password(self.password)
        user.save()
        self.forget_password.delete()
        return user
