from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView


class TetsApi(APIView):
    def get(self,request):
        print(request.user.id)
        return request.user