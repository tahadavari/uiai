from rest_framework.exceptions import PermissionDenied

from account.models import User
from rest_framework import serializers

from media.serializers import MediaRelatedField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'username']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class AuthorSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        data = {
            "id": instance.hash,
            "firstName": instance.first_name,
            "lastName": instance.last_name,
            "displayName": instance.first_name + " " + instance.last_name,
            "username":instance.username,
            "avatar": instance.avatar_url(),
            "banner": instance.banner_url(),
            "count": instance.posts.count(),
            "desc": instance.bio,
            "jobName": "نویسنده",
            "href": instance.href(),
        }
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'phone_number', 'avatar', 'username', 'email', 'banner']


class UpdateProfileSerializer(serializers.ModelSerializer):
    confirm_new_password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'phone_number', 'last_name', 'username',
                  'email', 'new_password', 'avatar', 'confirm_new_password', 'banner']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'new_password': {'required': False},
            'confirm_new_password': {'required': False},
            'username': {'required': True, 'allow_blank': False},
            'avatar': {'required': False},
            'banner': {'required': False},
            'phone_number': {'required': False}
        }

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_new_password'):
            raise PermissionDenied(
                {'confirm_new_password': ["Those passwords don't match."]})
        return data

    def save(self, **kwargs):
        user = super(UpdateProfileSerializer, self).save()
        if self.validated_data.get('new_password'):
            user.set_password(self.validated_data.get('new_password'))
        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'avatar', 'like_count', 'comment_count', 'bookmark_count', 'post_count', 'banner_url']

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count()

    def get_post_count(self, obj):
        return obj.posts.count()
