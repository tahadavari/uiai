from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.functions import add_append_user_to_data
from account.models import User
from core.permissions import IsAuthenticated
from media.serializers import PostImageSerializer


class UploadPostImageApi(APIView):
    def post(self, request):
        print('salam')
        request_data = {
            "user" : User.objects.all()[0].id,
            "image" : request.data.get('upload')
        }
        post_image_serializer = PostImageSerializer(data=request_data)
        post_image_serializer.is_valid(raise_exception=True)
        media = post_image_serializer.save()
        data = {
            "uploaded": 1,
            "fileName" : media.image.name.split('/')[-1],
            "url": media.url,  
        }
        return Response(data, status=status.HTTP_200_OK)
