from django.contrib.auth.models import Group

from rest_framework import serializers

from .models import User

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    Rank = serializers.SerializerMethodField(source = 'get_Rank_display') 
    CurrentUnit = serializers.CharField(source='CurrentUnit.ShortName',read_only=False,allow_null=True,default=None)
    groups = GroupSerializer(many=True, read_only=True)
    current_status = serializers.CharField(source='get_current_status_display', read_only=True)

    def get_Rank(self,obj):
        return obj.get_Rank_display()
    class Meta:
        model = User
        fields = [
                    'AFID',
                    'PersonID',
                    'FullName',
                    'Rank',
                    'first_name',
                    'last_name',
                    'Position',
                    'OfficePhone',
                    'MobilePhone',
                    'CurrentUnit',
                    'RTAFEMail',
                    'BirthDay',
                    'current_status',
                    'retire_date',
                    'groups'
                ]






