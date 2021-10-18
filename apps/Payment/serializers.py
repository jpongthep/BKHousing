from rest_framework import serializers

from .models import FinanceData


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