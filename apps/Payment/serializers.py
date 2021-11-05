from rest_framework import serializers

from .models import FinanceData, WaterPayment, RentPayment


class FinanceDataSerializer(serializers.ModelSerializer):   
    class Meta:
        model = FinanceData
        fields = [                    
                    "PersonID",
                    "date",
                    "code",
                    "money",
                    "comment",
        ]

class WaterPaymentSerializer(serializers.ModelSerializer):   
    class Meta:
        model = WaterPayment        
        fields = ['id','date','date_meter','meter','units','bill'] 

class RentPaymentSerializer(serializers.ModelSerializer):   
    class Meta:
        model = RentPayment
        fields = ['id','date','insurance_bill','montly_bill','method'] 
