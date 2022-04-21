from rest_framework import serializers

from media.models import PostImage


class MediaRelatedField(serializers.RelatedField):
    def to_native(self, value):
        return self.path


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image','user']
        extra_kwargs = {
            'image': {'required': True},
        }

