from rest_framework import serializers

from apps.Payment.serializers import WaterPaymentSerializer, RentPaymentSerializer
from apps.UserData.serializers import UserSerializer

from .models import HomeData, HomeOwner, CoResident, PetData, VehicalData

class ExpandSerializer(serializers.ModelSerializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(ExpandSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class HomeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(source = 'get_type_display') 
    zone = serializers.SerializerMethodField(source = 'get_zone_display') 
    status  = serializers.SerializerMethodField(source = 'get_status_display') 
    
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


class CoResidentSerializer(ExpandSerializer):
    relation_display = serializers.SerializerMethodField('get_relation')

    def get_relation(self,obj):
        return obj.get_relation_display()

    class Meta:
        model = CoResident
            
        fields = '__all__'
        extra_fields = ['relation_display']

class VehicalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicalData
        fields = '__all__'

class PetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetData
        fields = '__all__'


class HomeOwnerSerializer(serializers.ModelSerializer):

    home = HomeSerializer()
    WaterPayment = WaterPaymentSerializer(many=True, read_only=True)
    RentPayment = RentPaymentSerializer(many=True, read_only=True)
    owner = UserSerializer()
    co_resident = CoResidentSerializer(source='CoResident.all', many=True)
    vehical_data = VehicalDataSerializer(source='HomeParker.all', many=True)
    pet_data = PetDataSerializer(source='pet.all', many=True)
    # payment = PaymentDescSerializer(source='payments_project_desc.all', many=True)  
    status = serializers.SerializerMethodField('return_status')

    def return_status(self, obj):
        return "ok"

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
                    'RentPayment',
                    'co_resident',
                    'vehical_data',
                    'pet_data',
                    'status'
                ]


