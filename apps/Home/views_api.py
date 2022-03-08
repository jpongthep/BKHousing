import json
from django.shortcuts import render


from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import HomeOwner, CoResident, VehicalData, PetData
from .serializers import HomeOwnerSerializer, CoResidentSerializer, VehicalDataSerializer, PetDataSerializer
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
        # user = User.objects.get(username = "pongthep")
        home_owner = HomeOwner.objects.filter(owner = request.user).filter(is_stay = True)
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

    def get(self, request, pk = None, format=None):
        # print('request.user = ',request.user)
        # body = json.loads(request.body)
        # print("request.body = ",body)
        home_owner = HomeOwner.objects.filter(owner = request.user).filter(is_stay = True)
        cr = CoResident.objects.filter(home_owner = home_owner[0])
        if pk:
            cr = cr.filter(id = pk)
        serializer_context = {
            'request': request,
        }
        serializer = CoResidentSerializer(cr, many=True, context=serializer_context)
        return Response(serializer.data)

    def post(self, request, format=None):        
        try:
            if 'id' in request.data:                
                coresident = CoResident.objects.get(id = request.data['id'])
                serializer = CoResidentSerializer(coresident, data=request.data)   
                if serializer.is_valid():                             
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
        except:
            pass

        serializer = CoResidentSerializer(data=request.data)            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        coresident = CoResident.objects.get(id = pk)
        coresident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VehicalDataViewSet(APIView):

    def get(self, request, pk = None, format=None):
        # print('request.user = ',request.user)
        # body = json.loads(request.body)
        # print("request.body = ",body)
        home_parker = HomeOwner.objects.filter(owner = request.user).filter(is_stay = True)
        vd = VehicalData.objects.filter(home_parker = home_parker[0])
        if pk:
            vd = vd.filter(id = pk)
        serializer_context = {
            'request': request,
        }
        serializer = VehicalDataSerializer(vd, many=True, context=serializer_context)
        return Response(serializer.data)

    def post(self, request, format=None):    
        # print("request.data = ",request.data)    
        try:
            if 'id' in request.data:                
                vehical_data = VehicalData.objects.get(id = request.data['id'])
                serializer = VehicalDataSerializer(vehical_data, data=request.data)   
                if serializer.is_valid():                             
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
        except:
            pass

        serializer = VehicalDataSerializer(data=request.data)            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        vehical_data = VehicalData.objects.get(id = pk)
        vehical_data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class PetDataViewSet(APIView):

    def get(self, request, pk = None, format=None):
        # print('request.user = ',request.user)
        # body = json.loads(request.body)
        # print("request.body = ",body)
        home_owner = HomeOwner.objects.filter(owner = request.user).filter(is_stay = True)
        pd = PetData.objects.filter(home_owner = home_owner[0])
        if pk:
            pd = pd.filter(id = pk)
        serializer_context = {
            'request': request,
        }
        serializer = PetDataSerializer(pd, many=True, context=serializer_context)
        return Response(serializer.data)

    def post(self, request, format=None):        
        try:
            if 'id' in request.data:                
                pet_data = PetData.objects.get(id = request.data['id'])
                serializer = PetDataSerializer(pet_data, data=request.data)   
                if serializer.is_valid():                             
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
        except:
            pass

        serializer = PetDataSerializer(data=request.data)            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        pet_data = PetData.objects.get(id = pk)
        pet_data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
