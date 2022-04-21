from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string
from account.models import User, WriterRequest
from account.paginations import AuthorAllPagination
from blog.models import Post
from blog.paginations import PostsListProfileSetPagination
from blog.serializers import PostCardSerializer
from hashids import Hashids
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import AuthorSerializer, ProfileSerializer, UpdateProfileSerializer, UserInfoSerializer
from authenticate.models import EmailVerifyToken
from core.permissions import IsAuthenticated

from django.contrib.auth.hashers import check_password

from send_email.models import Email

hashids_verify_email = Hashids(salt=settings.EMAIL_VERIFY_SALT, min_length=10)


class ProfileGetApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer_user = ProfileSerializer(user)
        data = serializer_user.data
        return Response({'user': data})


class ProfileUpdateApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        change_email = False if request.user.email == request.data.get(
            'email') else True
        change_phone = False if request.user.phone_number == request.data.get(
            'phone_number') else True
        current_password = request.data.get('current_password')
        is_verify_current_password = check_password(
            current_password, request.user.password)
        if is_verify_current_password:
            serializer_user = UpdateProfileSerializer(user, request.data)
            serializer_user.is_valid(raise_exception=True)
            user_update = serializer_user.save()
            serializer_user = ProfileSerializer(user)
            data = serializer_user.data
            change_password = not check_password(
                current_password, user_update.password)
            if change_password or change_email or change_phone:
                if request.session.get('refresh-token'):
                    RefreshToken(request.session.get(
                        'refresh-token')).blacklist()
                    del request.session['refresh-token']

            if change_email:
                self.send_verify_email(user)
                user.verify_email = False
                user.save()
            if change_phone:
                user.level = User.LEVEL_COMMON
                user.verify_phone_number = False
                user.save()

            return Response(
                {'user': data, 'change_email': change_email, 'change_password': change_password, 'change_phone': change_phone, 'success': True})
        return Response({'error': 'رمز عبور وارد شده اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)

    def send_verify_email(self, user):
        if EmailVerifyToken.objects.filter(user=user).first():
            email_verify_token = EmailVerifyToken.objects.filter(
                user=user).first()
            token = email_verify_token.token
        else:
            token = hashids_verify_email.encode(
                int(user.id), datetime.now().microsecond)
            email_verify_token = EmailVerifyToken(user=user, token=token)
            email_verify_token.save()

        email_subject = "Activate your account"
        email_detail = {
            'first_name': user.first_name,
            'url': settings.EMAIL_VERIFY_URL + token
        }
        email_content = render_to_string(
            "email/email_verify.html", context=email_detail)
        email = Email(email_content=email_content, email_subject=email_subject, email_type=Email.TYPE_EMAIL_VERIFY,
                      receiver_email=user.email, email_detail=email_detail)
        email.save()
        email.send_email()


class UserInfoApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserInfoSerializer(user)
        data = user_serializer.data
        return Response(data, status=status.HTTP_200_OK)


class WriterRequestApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        writer_request = WriterRequest(user=user)
        writer_request.save()
        return Response({'success': True, 'message': 'درخاست شما با موفقیت ثبت شد'}, status=status.HTTP_200_OK)


class AuthorAll(generics.ListAPIView):
    queryset = User.objects.filter(level=User.LEVEL_WRITER)
    serializer_class = AuthorSerializer
    pagination_class = AuthorAllPagination


class AuthorView(generics.GenericAPIView):
    def get(self, request, username):

        if username.startswith('@'):
            username = username[1:]
        author = User.objects.get(username=username)
        data = AuthorSerializer(author).data
        return Response(data, status=status.HTTP_200_OK)


class BookmakPostProfile(generics.ListAPIView):
    serializer_class = PostCardSerializer
    pagination_class = PostsListProfileSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        posts_id = user.bookmarks.value_list('post', flat=True)
        posts = [Post.objects.get(id=x) for x in posts_id]
        return posts
