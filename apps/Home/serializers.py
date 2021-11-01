from rest_framework import serializers

from apps.Payment.serializers import WaterPaymentSerializer
from .models import HomeOwner



class HomeOwnerSerializer(serializers.ModelSerializer):

    WaterPayment = WaterPaymentSerializer()
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
                    'WaterPayment'
                ]


