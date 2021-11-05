from rest_framework import serializers

from apps.Payment.serializers import WaterPaymentSerializer, RentPaymentSerializer
from apps.UserData.serializers import UserSerializer

from .models import HomeData, HomeOwner



class HomeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(source = 'get_type_display') 
    zone = serializers.SerializerMethodField(source = 'get_zone_display') 
    status = serializers.SerializerMethodField(source = 'get_status_display') 
    
    def get_type(self,obj):
        return obj.get_type_display()

    def get_zone(self,obj):
        return obj.get_zone_display()
    
    def get_status(self,obj):
        return obj.get_status_display()
        
    class Meta:
        model = HomeData
        fields = [
                    "type",
                    "zone",
                    "location_name",
                    "building_number",
                    "room_number",
                    "number",
                    "status",
                    "monthly_fee",
                    "enter_fee",
                ]

class HomeOwnerSerializer(serializers.ModelSerializer):

    home = HomeSerializer()
    WaterPayment = WaterPaymentSerializer(many=True, read_only=True)
    RentPayment = RentPaymentSerializer(many=True, read_only=True)
    owner = UserSerializer()
    class Meta:
        model = HomeOwner
        fields = [
                    'owner',
                    'home',
                    'is_stay',
                    'enter_command',
                    'date_enter',
                    'leave_command',
                    'date_leave',
                    'leave_type',
                    'leave_comment',
                    'insurance_rate',
                    'rent_rate',
                    'water_meter_insurance',
                    'water_meter',
                    'electric_meter',
                    'WaterPayment',
                    'RentPayment'
                ]


