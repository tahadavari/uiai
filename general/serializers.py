from rest_framework import serializers



class TeamsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        data = {
            'id': instance.hash,
            'name': instance.name,
            'job': instance.description,
            'avatar': instance.avatar_url()
        },
        return data


class SocialSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "name": instance.name,
            "icon": instance.icon,
            "href": instance.link,
        }
        return data
