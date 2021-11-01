from rest_framework import serializers

from .models import FinanceData, WaterPayment


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

class WaterPaymentSerializer(serializers.HyperlinkedModelSerializer):   
    class Meta:
        model = WaterPayment
        fields = '__all__' 
