import json
from django.shortcuts import render


from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import HomeOwner, CoResident
from .serializers import HomeOwnerSerializer, CoResidentSerializer
from apps.UserData.models import User

class HomeOwnerViewSet(APIView):
    """
    List all ProjectDescS, or create a new ProjectDesc.
    """
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # print('request.user = ',request.user)
        # body = json.loads(request.body)
        # print("request.body = ",body)
        user = User.objects.get(username = "pongthep")
        home_owner = HomeOwner.objects.filter(owner = user).filter(is_stay = True)
        serializer_context = {
            'request': request,
        }
        serializer = HomeOwnerSerializer(home_owner, many=True, context=serializer_context)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HomeOwnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoResidentViewSet(APIView):

    def get(self, request, format=None):
        # print('request.user = ',request.user)
        # body = json.loads(request.body)
        # print("request.body = ",body)
        user = User.objects.get(username = "pongthep")
        home_owner = HomeOwner.objects.filter(owner = user).filter(is_stay = True)
        cr = CoResident.objects.filter(home_owner = home_owner[0])
        serializer_context = {
            'request': request,
        }
        serializer = CoResidentSerializer(cr, many=True, context=serializer_context)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CoResidentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)