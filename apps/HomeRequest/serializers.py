from rest_framework import serializers

from .models import HomeRequest


class HomeRequestSerializer(serializers.ModelSerializer):
    UnitName = serializers.CharField(source='Requester.CurrentUnit.ShortName',read_only=False,allow_null=True,default=None)
    MobilePhone = serializers.CharField(source='Requester.MobilePhone')
    UnitRecieverName = serializers.CharField(source='UnitReciever.FullName',read_only=False,allow_null=True,default=None)
    UnitRecieverPhone = serializers.CharField(source='UnitReciever.OfficePhone',read_only=False,allow_null=True,default=None)
    UnitApproverName = serializers.CharField(source='UnitApprover.FullName',read_only=False,allow_null=True,default=None)
    UnitApproverPhone = serializers.CharField(source='UnitApprover.OfficePhone',read_only=False,allow_null=True,default=None)
    PersonApproverName = serializers.CharField(source='PersonApprover.FullName',read_only=False,allow_null=True,default=None)
    PersonApproverPhone = serializers.CharField(source='PersonApprover.OfficePhone',read_only=False,allow_null=True,default=None)
    PersonRecieverName = serializers.CharField(source='PersonReciever.FullName',read_only=False,allow_null=True,default=None)
    PersonRecieverPhone = serializers.CharField(source='PersonReciever.OfficePhone',read_only=False,allow_null=True,default=None)

    class Meta:
        model = HomeRequest
        fields = [
                    "id", 
                    "FullName", 
                    "UnitName", 
                    "MobilePhone", 
                    "Position",
                    "ProcessStep",
                    "RequesterDateSend",

                    "UnitReciever",
                    "UnitRecieverName",
                    "UnitRecieverPhone",
                    "UnitDateRecieved",

                    "UnitApprover",
                    "UnitApproverName",
                    "UnitApproverPhone",
                    "UnitDateApproved",

                    "PersonReciever",
                    "PersonRecieverName",
                    "PersonRecieverPhone",
                    "PersonDateRecieved",

                    "PersonApprover",
                    "PersonApproverName",
                    "PersonApproverPhone",
                    "PersonDateApproved",

                    "IsUnitEval",
                    "UnitTroubleScore",
                    "IsPersonEval",
                    "PersonTroubleScore",
                    "TroubleScore"
        ]